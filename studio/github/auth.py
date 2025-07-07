"""
GitHub Authentication Module
Handles OAuth flow and token management for GitHub API access
"""

import os
import json
import webbrowser
import keyring
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
import aiohttp
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from cryptography.fernet import Fernet
import base64

console = Console()

class GitHubAuth:
    """GitHub Authentication Handler"""
    
    def __init__(self):
        # Read from environment variables or use defaults
        self.client_id = os.getenv('GITHUB_CLIENT_ID', "your_github_oauth_app_client_id")
        self.client_secret = os.getenv('GITHUB_CLIENT_SECRET', "your_github_oauth_app_client_secret")
        self.redirect_uri = "http://localhost:8080/callback"
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.api_base = "https://api.github.com"
        self.access_token = None
        self.user_info = None
        self.config_dir = Path.home() / ".gitflow-studio"
        self.config_file = self.config_dir / "github_config.json"
        self._encryption_key = None
        
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key for storing tokens securely"""
        if self._encryption_key is None:
            key_name = "gitflow_studio_github_key"
            stored_key = keyring.get_password("gitflow_studio", key_name)
            
            if stored_key:
                self._encryption_key = base64.urlsafe_b64decode(stored_key)
            else:
                # Generate new key
                new_key = Fernet.generate_key()
                keyring.set_password("gitflow_studio", key_name, base64.urlsafe_b64encode(new_key).decode())
                self._encryption_key = new_key
                
        return self._encryption_key
    
    def _encrypt_token(self, token: str) -> str:
        """Encrypt token for secure storage"""
        f = Fernet(self._get_encryption_key())
        return f.encrypt(token.encode()).decode()
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt token from secure storage"""
        f = Fernet(self._get_encryption_key())
        return f.decrypt(encrypted_token.encode()).decode()
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        self.config_dir.mkdir(exist_ok=True)
        
        # Encrypt sensitive data
        if 'access_token' in config:
            config['access_token'] = self._encrypt_token(config['access_token'])
            
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file.exists():
            return {}
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            # Decrypt sensitive data
            if 'access_token' in config:
                config['access_token'] = self._decrypt_token(config['access_token'])
                
            return config
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load config: {e}[/]")
            return {}
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        config = self._load_config()
        if 'access_token' not in config:
            return False
            
        self.access_token = config['access_token']
        self.user_info = config.get('user_info')
        
        # Check if token is still valid
        return self.access_token is not None
    
    async def login(self) -> bool:
        """Perform GitHub OAuth login flow"""
        # Check if credentials are configured
        if (self.client_id == "your_github_oauth_app_client_id" or 
            self.client_secret == "your_github_oauth_app_client_secret"):
            console.print(Panel("""
[bold red]❌ GitHub OAuth credentials not configured![/]

To use GitHub authentication, you need to:

1. Create a GitHub OAuth App:
   - Go to GitHub Settings > Developer settings > OAuth Apps
   - Click "New OAuth App"
   - Set Application name: "GitFlow Studio"
   - Set Homepage URL: "http://localhost:8080"
   - Set Authorization callback URL: "http://localhost:8080/callback"

2. Set environment variables:
   export GITHUB_CLIENT_ID="your_client_id_here"
   export GITHUB_CLIENT_SECRET="your_client_secret_here"

3. Or update the auth.py file directly with your credentials.

See studio/github/config_template.py for detailed instructions.
            """, title="[red]Configuration Required", border_style="red"))
            return False
        
        console.print(Panel("[bold blue]GitHub Authentication[/]\n[dim]You will be redirected to GitHub to authorize GitFlow Studio[/]", 
                          title="[green]Login", border_style="green"))
        
        # Generate state parameter for security
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Build authorization URL
        auth_params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'repo user',
            'state': state
        }
        
        auth_url = f"{self.auth_url}?{'&'.join(f'{k}={v}' for k, v in auth_params.items())}"
        
        console.print(f"[cyan]Opening browser for GitHub authorization...[/]")
        console.print(f"[dim]If browser doesn't open, visit: {auth_url}[/]")
        
        # Open browser
        try:
            webbrowser.open(auth_url)
        except Exception as e:
            console.print(f"[yellow]Could not open browser: {e}[/]")
            console.print(f"[cyan]Please visit: {auth_url}[/]")
        
        # Start local server to receive callback
        code = await self._start_callback_server(state)
        
        if not code:
            console.print("[red]Authentication cancelled or failed[/]")
            return False
        
        # Exchange code for access token
        token = await self._exchange_code_for_token(code)
        
        if not token:
            console.print("[red]Failed to obtain access token[/]")
            return False
        
        # Get user information
        user_info = await self._get_user_info(token)
        
        if not user_info:
            console.print("[red]Failed to get user information[/]")
            return False
        
        # Save configuration
        config = {
            'access_token': token,
            'user_info': user_info,
            'authenticated_at': datetime.now().isoformat()
        }
        self._save_config(config)
        
        self.access_token = token
        self.user_info = user_info
        
        console.print(Panel(f"[bold green]✅ Successfully authenticated as {user_info['login']}![/]", 
                          title="[green]Success", border_style="green"))
        return True
    
    async def _start_callback_server(self, expected_state: str) -> Optional[str]:
        """Start local server to receive OAuth callback"""
        from aiohttp import web
        
        code = None
        state_received = None
        
        async def callback_handler(request):
            nonlocal code, state_received
            
            params = request.query
            code = params.get('code')
            state_received = params.get('state')
            error = params.get('error')
            
            if error:
                html = f"""
                <html>
                    <body>
                        <h2>Authentication Error</h2>
                        <p>Error: {error}</p>
                        <p>You can close this window.</p>
                    </body>
                </html>
                """
            else:
                html = """
                <html>
                    <body>
                        <h2>Authentication Successful!</h2>
                        <p>You have been successfully authenticated with GitHub.</p>
                        <p>You can close this window and return to the terminal.</p>
                    </body>
                </html>
                """
            
            return web.Response(text=html, content_type='text/html')
        
        app = web.Application()
        app.router.add_get('/callback', callback_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()
        
        # Wait for callback
        timeout = 300  # 5 minutes
        start_time = datetime.now()
        
        while not code and (datetime.now() - start_time).seconds < timeout:
            await asyncio.sleep(1)
        
        await runner.cleanup()
        
        if state_received != expected_state:
            console.print("[red]State mismatch - possible CSRF attack[/]")
            return None
            
        return code
    
    async def _exchange_code_for_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for access token"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Exchanging code for access token...", total=None)
            
            async with aiohttp.ClientSession() as session:
                data = {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': code,
                    'redirect_uri': self.redirect_uri
                }
                
                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
                
                async with session.post(self.token_url, json=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        token = result.get('access_token')
                        progress.update(task, description="✅ Access token obtained!")
                        return token
                    else:
                        progress.update(task, description="❌ Failed to get access token")
                        return None
    
    async def _get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get authenticated user information"""
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            async with session.get(f"{self.api_base}/user", headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
    
    def logout(self):
        """Logout and clear stored credentials"""
        try:
            # Clear stored token
            keyring.delete_password("gitflow_studio", "github_token")
            
            # Remove config file
            if self.config_file.exists():
                self.config_file.unlink()
            
            self.access_token = None
            self.user_info = None
            
            console.print(Panel("[bold green]✅ Successfully logged out from GitHub[/]", 
                              title="[green]Logout", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error during logout:[/] {e}", 
                              title="[red]Error", border_style="red"))
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user information"""
        return self.user_info
    
    def get_access_token(self) -> Optional[str]:
        """Get current access token"""
        return self.access_token 