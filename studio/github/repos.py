"""
GitHub Repositories Module
Handles repository listing, cloning, and management via GitHub API
"""

import os
import asyncio
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiohttp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich import box

from .auth import GitHubAuth

console = Console()

class GitHubRepos:
    """GitHub Repository Manager"""
    
    def __init__(self, auth: GitHubAuth):
        self.auth = auth
        self.api_base = "https://api.github.com"
        
    async def list_repositories(self, user_type: str = "user") -> List[Dict[str, Any]]:
        """List repositories for the authenticated user"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching repositories...", total=None)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                # Get user repositories
                url = f"{self.api_base}/user/repos"
                params = {
                    'type': user_type,  # 'all', 'owner', 'member'
                    'sort': 'updated',
                    'per_page': 100
                }
                
                repos = []
                page = 1
                
                while True:
                    params['page'] = page
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            page_repos = await response.json()
                            if not page_repos:
                                break
                            repos.extend(page_repos)
                            page += 1
                        else:
                            progress.update(task, description="❌ Failed to fetch repositories")
                            return []
                
                progress.update(task, description=f"✅ Found {len(repos)} repositories!")
                return repos
    
    def display_repositories(self, repos: List[Dict[str, Any]]):
        """Display repositories in a nice table format"""
        if not repos:
            console.print(Panel("[yellow]No repositories found.[/]", 
                              title="[blue]Repositories", border_style="blue"))
            return
        
        table = Table(
            title=f"[bold blue]GitHub Repositories[/]\n[dim]Found {len(repos)} repositories[/]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="blue"
        )
        
        table.add_column("#", style="cyan", no_wrap=True)
        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Owner", style="yellow", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Language", style="cyan", no_wrap=True)
        table.add_column("Stars", style="yellow", no_wrap=True)
        table.add_column("Updated", style="dim", no_wrap=True)
        
        for i, repo in enumerate(repos, 1):
            name = repo['name']
            owner = repo['owner']['login']
            description = repo.get('description', '')[:50] + '...' if repo.get('description', '') and len(repo.get('description', '')) > 50 else repo.get('description', 'No description')
            language = repo.get('language', 'N/A')
            stars = repo.get('stargazers_count', 0)
            updated = repo['updated_at'][:10]  # Just the date part
            
            table.add_row(
                f"[bold]{i}[/]",
                f"[bold green]{name}[/]",
                owner,
                description,
                language,
                str(stars),
                updated
            )
        
        console.print(table)
    
    async def clone_repository(self, repo_name: str, target_path: Optional[str] = None) -> bool:
        """Clone a repository by name"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return False
        
        # Find repository
        repos = await self.list_repositories()
        target_repo = None
        
        for repo in repos:
            if repo['name'] == repo_name:
                target_repo = repo
                break
        
        if not target_repo:
            console.print(Panel(f"[bold red]❌ Repository '{repo_name}' not found.[/]", 
                              title="[red]Error", border_style="red"))
            return False
        
        # Determine clone path
        if not target_path:
            user_info = self.auth.get_user_info()
            if user_info:
                default_path = Path.home() / "git" / user_info['login'] / repo_name
            else:
                default_path = Path.home() / "git" / repo_name
            
            target_path = Prompt.ask(
                "Clone to path",
                default=str(default_path)
            )
        
        target_path_obj = Path(target_path)
        
        # Create directory if it doesn't exist
        target_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Clone repository
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Cloning {repo_name}...", total=None)
            
            try:
                # Use HTTPS URL for authenticated cloning
                clone_url = target_repo['clone_url']
                
                # Replace with authenticated URL if it's a private repo
                if target_repo['private']:
                    token = self.auth.get_access_token()
                    clone_url = clone_url.replace('https://', f'https://{token}@')
                
                result = subprocess.run(
                    ['git', 'clone', clone_url, str(target_path_obj)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    progress.update(task, description=f"✅ Successfully cloned {repo_name}!")
                    console.print(Panel(f"[bold green]✅ Repository '{repo_name}' cloned successfully![/]\n[dim]Path: {target_path_obj}[/]", 
                                      title="[green]Success", border_style="green"))
                    return True
                else:
                    progress.update(task, description=f"❌ Failed to clone {repo_name}")
                    console.print(Panel(f"[bold red]❌ Failed to clone repository:[/]\n{result.stderr}", 
                                      title="[red]Error", border_style="red"))
                    return False
                    
            except subprocess.TimeoutExpired:
                progress.update(task, description="❌ Clone operation timed out")
                console.print(Panel("[bold red]❌ Clone operation timed out[/]", 
                                  title="[red]Error", border_style="red"))
                return False
            except Exception as e:
                progress.update(task, description=f"❌ Error: {e}")
                console.print(Panel(f"[bold red]❌ Error during clone:[/] {e}", 
                                  title="[red]Error", border_style="red"))
                return False
    
    async def search_repositories(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search repositories on GitHub"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Searching for '{query}'...", total=None)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                url = f"{self.api_base}/search/repositories"
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': min(limit, 100)
                }
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        repos = result.get('items', [])
                        progress.update(task, description=f"✅ Found {len(repos)} repositories!")
                        return repos
                    else:
                        progress.update(task, description="❌ Search failed")
                        return []
    
    async def get_repository_info(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific repository"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return None
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Fetching info for {owner}/{repo}...", total=None)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                url = f"{self.api_base}/repos/{owner}/{repo}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        repo_info = await response.json()
                        progress.update(task, description=f"✅ Got info for {owner}/{repo}!")
                        return repo_info
                    else:
                        progress.update(task, description="❌ Failed to get repository info")
                        return None
    
    def display_repository_info(self, repo_info: Dict[str, Any]):
        """Display detailed repository information"""
        info = f"""
[bold blue]Repository Information[/]

[bright_blue]Name:[/] {repo_info['full_name']}
[bright_blue]Description:[/] {repo_info.get('description', 'No description')}
[bright_blue]Language:[/] {repo_info.get('language', 'N/A')}
[bright_blue]Stars:[/] {repo_info.get('stargazers_count', 0)}
[bright_blue]Forks:[/] {repo_info.get('forks_count', 0)}
[bright_blue]Watchers:[/] {repo_info.get('watchers_count', 0)}
[bright_blue]Private:[/] {'Yes' if repo_info['private'] else 'No'}
[bright_blue]Created:[/] {repo_info['created_at'][:10]}
[bright_blue]Updated:[/] {repo_info['updated_at'][:10]}
[bright_blue]Clone URL:[/] {repo_info['clone_url']}
[bright_blue]SSH URL:[/] {repo_info.get('ssh_url', 'N/A')}
        """
        
        console.print(Panel(info, title="[green]Repository Details", border_style="green"))
    
    async def list_issues(self, repo_full_name: str, state: str = 'open', limit: int = 20, label: str = '', assignee: str = ''):
        """List issues for a given repository, with optional label and assignee filters"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Fetching issues for {repo_full_name}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/issues"
                params = {
                    'state': state,
                    'per_page': min(limit, 100),
                    'page': 1
                }
                if label is not None:
                    params['labels'] = label
                if assignee is not None:
                    params['assignee'] = assignee
                issues = []
                while len(issues) < limit:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            page_issues = await response.json()
                            if not page_issues:
                                break
                            issues.extend(page_issues)
                            if len(page_issues) < params['per_page']:
                                break
                            params['page'] += 1
                        else:
                            progress.update(task, description="❌ Failed to fetch issues")
                            console.print(Panel(f"[bold red]❌ Failed to fetch issues: {response.status}[/]", 
                                              title="[red]Error", border_style="red"))
                            return
                progress.update(task, description=f"✅ Found {len(issues)} issues!")
                # Display issues (unchanged)
                if not issues:
                    console.print(Panel("[yellow]No issues found.[/]", 
                                      title="[blue]Issues", border_style="blue"))
                    return
                table = Table(
                    title=f"[bold blue]GitHub Issues[/]\n[dim]Found {len(issues)} issues[/]",
                    show_header=True,
                    header_style="bold magenta",
                    box=box.ROUNDED,
                    border_style="blue"
                )
                table.add_column("#", style="cyan", no_wrap=True)
                table.add_column("Title", style="green")
                table.add_column("State", style="yellow")
                table.add_column("User", style="white")
                table.add_column("Created", style="dim")
                table.add_column("URL", style="blue")
                for i, issue in enumerate(issues[:limit], 1):
                    table.add_row(
                        f"[bold]{i}[/]",
                        issue.get('title', 'No title'),
                        issue.get('state', ''),
                        issue.get('user', {}).get('login', ''),
                        issue.get('created_at', '')[:10],
                        issue.get('html_url', '')
                    )
                console.print(table)

    async def comment_issue(self, repo_full_name: str, issue_number: int, body: str):
        """Comment on a GitHub issue"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Commenting on issue #{issue_number}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/issues/{issue_number}/comments"
                data = {'body': body}
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 201:
                        comment = await response.json()
                        progress.update(task, description="✅ Comment posted!")
                        console.print(Panel(f"[bold green]✅ Comment posted![/]\n[dim]URL:[/] {comment.get('html_url', '')}", 
                                          title="[green]Success", border_style="green"))
                    else:
                        error_text = await response.text()
                        progress.update(task, description="❌ Failed to post comment")
                        console.print(Panel(f"[bold red]❌ Failed to post comment: {response.status}[/]\n{error_text}", 
                                          title="[red]Error", border_style="red"))

    async def close_issue(self, repo_full_name: str, issue_number: int):
        """Close a GitHub issue"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Closing issue #{issue_number}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/issues/{issue_number}"
                data = {'state': 'closed'}
                async with session.patch(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        issue = await response.json()
                        progress.update(task, description="✅ Issue closed!")
                        console.print(Panel(f"[bold green]✅ Issue closed![/]\n[dim]URL:[/] {issue.get('html_url', '')}", 
                                          title="[green]Success", border_style="green"))
                    else:
                        error_text = await response.text()
                        progress.update(task, description="❌ Failed to close issue")
                        console.print(Panel(f"[bold red]❌ Failed to close issue: {response.status}[/]\n{error_text}", 
                                          title="[red]Error", border_style="red"))

    async def assign_issue(self, repo_full_name: str, issue_number: int, user: str):
        """Assign a user to a GitHub issue"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Assigning @{user} to issue #{issue_number}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/issues/{issue_number}/assignees"
                data = {'assignees': [user]}
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status in (200, 201):
                        progress.update(task, description="✅ User assigned!")
                        console.print(Panel(f"[bold green]✅ User assigned to issue![/]", 
                                          title="[green]Success", border_style="green"))
                    else:
                        error_text = await response.text()
                        progress.update(task, description="❌ Failed to assign user")
                        console.print(Panel(f"[bold red]❌ Failed to assign user: {response.status}[/]\n{error_text}", 
                                          title="[red]Error", border_style="red"))

    async def label_issue(self, repo_full_name: str, issue_number: int, label: str):
        """Add a label to a GitHub issue"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Adding label '{label}' to issue #{issue_number}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/issues/{issue_number}/labels"
                data = {'labels': [label]}
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status in (200, 201):
                        progress.update(task, description="✅ Label added!")
                        console.print(Panel(f"[bold green]✅ Label added to issue![/]", 
                                          title="[green]Success", border_style="green"))
                    else:
                        error_text = await response.text()
                        progress.update(task, description="❌ Failed to add label")
                        console.print(Panel(f"[bold red]❌ Failed to add label: {response.status}[/]\n{error_text}", 
                                          title="[red]Error", border_style="red"))

    async def create_issue(self, repo_full_name: str, title: str, body: str = ""):
        """Create a new issue for a given repository"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Creating issue in {repo_full_name}...", total=None)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                url = f"{self.api_base}/repos/{repo_full_name}/issues"
                data = {
                    'title': title,
                    'body': body or ""
                }
                
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 201:
                        issue = await response.json()
                        progress.update(task, description="✅ Issue created!")
                        console.print(Panel(f"[bold green]✅ Issue created successfully![/]\n[dim]URL:[/] {issue.get('html_url', '')}", 
                                          title="[green]Success", border_style="green"))
                    else:
                        error_text = await response.text()
                        progress.update(task, description="❌ Failed to create issue")
                        console.print(Panel(f"[bold red]❌ Failed to create issue: {response.status}[/]\n{error_text}", 
                                          title="[red]Error", border_style="red"))

    async def list_pull_requests(self, repo_full_name: str, state: str = 'open', limit: int = 20, label: str = '', assignee: str = ''):
        """List pull requests for a given repository, with optional label and assignee filters"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Fetching pull requests for {repo_full_name}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/pulls"
                params = {
                    'state': state,
                    'per_page': min(limit, 100),
                    'page': 1
                }
                if label is not None:
                    params['labels'] = label
                if assignee is not None:
                    params['assignee'] = assignee
                prs = []
                while len(prs) < limit:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            page_prs = await response.json()
                            if not page_prs:
                                break
                            prs.extend(page_prs)
                            if len(page_prs) < params['per_page']:
                                break
                            params['page'] += 1
                        else:
                            progress.update(task, description="❌ Failed to fetch pull requests")
                            console.print(Panel(f"[bold red]❌ Failed to fetch pull requests: {response.status}[/]", 
                                              title="[red]Error", border_style="red"))
                            return
                progress.update(task, description=f"✅ Found {len(prs)} pull requests!")
                # Display PRs
                if not prs:
                    console.print(Panel("[yellow]No pull requests found.[/]", 
                                      title="[blue]Pull Requests", border_style="blue"))
                    return
                table = Table(
                    title=f"[bold blue]GitHub Pull Requests[/]\n[dim]Found {len(prs)} pull requests[/]",
                    show_header=True,
                    header_style="bold magenta",
                    box=box.ROUNDED,
                    border_style="blue"
                )
                table.add_column("#", style="cyan", no_wrap=True)
                table.add_column("Title", style="green")
                table.add_column("State", style="yellow")
                table.add_column("User", style="white")
                table.add_column("Created", style="dim")
                table.add_column("URL", style="blue")
                for i, pr in enumerate(prs[:limit], 1):
                    table.add_row(
                        f"[bold]{i}[/]",
                        pr.get('title', 'No title'),
                        pr.get('state', ''),
                        pr.get('user', {}).get('login', ''),
                        pr.get('created_at', '')[:10],
                        pr.get('html_url', '')
                    )
                console.print(table)

    async def create_pull_request(self, repo_full_name: str, title: str, head: str, base: str, body: str = ""):
        """Create a new pull request"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Creating pull request in {repo_full_name}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/pulls"
                data = {
                    'title': title,
                    'head': head,
                    'base': base,
                    'body': body or ""
                }
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 201:
                        pr = await response.json()
                        progress.update(task, description="✅ Pull request created!")
                        console.print(Panel(f"[bold green]✅ Pull request created successfully![/]\n[dim]URL:[/] {pr.get('html_url', '')}", 
                                          title="[green]Success", border_style="green"))
                    else:
                        error_text = await response.text()
                        progress.update(task, description="❌ Failed to create pull request")
                        console.print(Panel(f"[bold red]❌ Failed to create pull request: {response.status}[/]\n{error_text}", 
                                          title="[red]Error", border_style="red"))

    async def comment_pull_request(self, repo_full_name: str, pr_number: int, body: str):
        """Comment on a pull request (issue comments API)"""
        await self.comment_issue(repo_full_name, pr_number, body)

    async def close_pull_request(self, repo_full_name: str, pr_number: int):
        """Close a pull request"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Closing pull request #{pr_number}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/pulls/{pr_number}"
                data = {'state': 'closed'}
                async with session.patch(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        pr = await response.json()
                        progress.update(task, description="✅ Pull request closed!")
                        console.print(Panel(f"[bold green]✅ Pull request closed![/]\n[dim]URL:[/] {pr.get('html_url', '')}", 
                                          title="[green]Success", border_style="green"))
                    else:
                        error_text = await response.text()
                        progress.update(task, description="❌ Failed to close pull request")
                        console.print(Panel(f"[bold red]❌ Failed to close pull request: {response.status}[/]\n{error_text}", 
                                          title="[red]Error", border_style="red"))

    async def merge_pull_request(self, repo_full_name: str, pr_number: int, method: str = 'merge'):
        """Merge a pull request"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Merging pull request #{pr_number}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/pulls/{pr_number}/merge"
                data = {'merge_method': method}
                async with session.put(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        merge_result = await response.json()
                        progress.update(task, description="✅ Pull request merged!")
                        console.print(Panel(f"[bold green]✅ Pull request merged![/]\n[dim]Message:[/] {merge_result.get('message', '')}", 
                                          title="[green]Success", border_style="green"))
                    else:
                        error_text = await response.text()
                        progress.update(task, description="❌ Failed to merge pull request")
                        console.print(Panel(f"[bold red]❌ Failed to merge pull request: {response.status}[/]\n{error_text}", 
                                          title="[red]Error", border_style="red"))

    async def assign_pull_request(self, repo_full_name: str, pr_number: int, user: str):
        """Assign a user to a pull request (issue assignees API)"""
        await self.assign_issue(repo_full_name, pr_number, user)

    async def label_pull_request(self, repo_full_name: str, pr_number: int, label: str):
        """Add a label to a pull request (issue labels API)"""
        await self.label_issue(repo_full_name, pr_number, label)

    async def list_notifications(self, all: bool = False):
        """List GitHub notifications (unread by default, all if requested)"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching notifications...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/notifications"
                params = {'all': str(all).lower()}
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        notifications = await response.json()
                        progress.update(task, description=f"✅ Found {len(notifications)} notifications!")
                        if not notifications:
                            console.print(Panel("[yellow]No notifications found.[/]", 
                                              title="[blue]Notifications", border_style="blue"))
                            return
                        table = Table(
                            title=f"[bold blue]GitHub Notifications[/]\n[dim]Found {len(notifications)} notifications[/]",
                            show_header=True,
                            header_style="bold magenta",
                            box=box.ROUNDED,
                            border_style="blue"
                        )
                        table.add_column("#", style="cyan", no_wrap=True)
                        table.add_column("Reason", style="green")
                        table.add_column("Repository", style="yellow")
                        table.add_column("Subject", style="white")
                        table.add_column("Type", style="dim")
                        table.add_column("Updated", style="blue")
                        table.add_column("ID", style="magenta")
                        for i, n in enumerate(notifications, 1):
                            table.add_row(
                                f"[bold]{i}[/]",
                                n.get('reason', ''),
                                n.get('repository', {}).get('full_name', ''),
                                n.get('subject', {}).get('title', ''),
                                n.get('subject', {}).get('type', ''),
                                n.get('updated_at', '')[:10],
                                n.get('id', '')
                            )
                        console.print(table)
                    else:
                        error_text = await response.text()
                        progress.update(task, description="❌ Failed to fetch notifications")
                        console.print(Panel(f"[bold red]❌ Failed to fetch notifications: {response.status}[/]\n{error_text}", 
                                          title="[red]Error", border_style="red"))

    async def mark_notifications_as_read(self, thread_id: str = '', mark_all: bool = False):
        """Mark notifications as read (all or by thread ID)"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            if mark_all:
                task = progress.add_task("Marking all notifications as read...", total=None)
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'Authorization': f'token {self.auth.get_access_token()}',
                        'Accept': 'application/vnd.github.v3+json'
                    }
                    url = f"{self.api_base}/notifications"
                    async with session.put(url, headers=headers) as response:
                        if response.status == 205:
                            progress.update(task, description="✅ All notifications marked as read!")
                            console.print(Panel("[bold green]✅ All notifications marked as read![/]", 
                                              title="[green]Success", border_style="green"))
                        else:
                            error_text = await response.text()
                            progress.update(task, description="❌ Failed to mark all as read")
                            console.print(Panel(f"[bold red]❌ Failed to mark all as read: {response.status}[/]\n{error_text}", 
                                              title="[red]Error", border_style="red"))
            elif thread_id:
                task = progress.add_task(f"Marking notification {thread_id} as read...", total=None)
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'Authorization': f'token {self.auth.get_access_token()}',
                        'Accept': 'application/vnd.github.v3+json'
                    }
                    url = f"{self.api_base}/notifications/threads/{thread_id}"
                    async with session.patch(url, headers=headers) as response:
                        if response.status == 205:
                            progress.update(task, description="✅ Notification marked as read!")
                            console.print(Panel(f"[bold green]✅ Notification {thread_id} marked as read![/]", 
                                              title="[green]Success", border_style="green"))
                        else:
                            error_text = await response.text()
                            progress.update(task, description="❌ Failed to mark as read")
                            console.print(Panel(f"[bold red]❌ Failed to mark as read: {response.status}[/]\n{error_text}", 
                                              title="[red]Error", border_style="red"))
            else:
                console.print(Panel("[bold red]❌ Please specify a thread ID or use --all to mark all as read.[/]", 
                                  title="[red]Error", border_style="red"))

    async def list_releases(self, repo_full_name: str, limit: int = 20):
        """List releases for a given repository"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Fetching releases for {repo_full_name}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/releases"
                params = {'per_page': min(limit, 100), 'page': 1}
                releases = []
                while len(releases) < limit:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            page_releases = await response.json()
                            if not page_releases:
                                break
                            releases.extend(page_releases)
                            if len(page_releases) < params['per_page']:
                                break
                            params['page'] += 1
                        else:
                            progress.update(task, description="❌ Failed to fetch releases")
                            console.print(Panel(f"[bold red]❌ Failed to fetch releases: {response.status}[/]", 
                                              title="[red]Error", border_style="red"))
                            return
                progress.update(task, description=f"✅ Found {len(releases)} releases!")
                # Display releases
                if not releases:
                    console.print(Panel("[yellow]No releases found.[/]", 
                                      title="[blue]Releases", border_style="blue"))
                    return
                table = Table(
                    title=f"[bold blue]GitHub Releases[/]\n[dim]Found {len(releases)} releases[/]",
                    show_header=True,
                    header_style="bold magenta",
                    box=box.ROUNDED,
                    border_style="blue"
                )
                table.add_column("#", style="cyan", no_wrap=True)
                table.add_column("Tag", style="green")
                table.add_column("Title", style="yellow")
                table.add_column("Draft", style="white")
                table.add_column("Prerelease", style="dim")
                table.add_column("Created", style="blue")
                table.add_column("URL", style="magenta")
                for i, rel in enumerate(releases[:limit], 1):
                    table.add_row(
                        f"[bold]{i}[/]",
                        rel.get('tag_name', ''),
                        rel.get('name', ''),
                        str(rel.get('draft', False)),
                        str(rel.get('prerelease', False)),
                        rel.get('created_at', '')[:10],
                        rel.get('html_url', '')
                    )
                console.print(table)

    async def create_release(self, repo_full_name: str, tag: str, title: str, body: str = '', draft: bool = False, prerelease: bool = False):
        """Create a new release for a given repository"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Creating release in {repo_full_name}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                url = f"{self.api_base}/repos/{repo_full_name}/releases"
                data = {
                    'tag_name': tag,
                    'name': title,
                    'body': body or '',
                    'draft': draft,
                    'prerelease': prerelease
                }
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 201:
                        release = await response.json()
                        progress.update(task, description="✅ Release created!")
                        console.print(Panel(f"[bold green]✅ Release created successfully![/]\n[dim]URL:[/] {release.get('html_url', '')}", 
                                          title="[green]Success", border_style="green"))
                    else:
                        error_text = await response.text()
                        progress.update(task, description="❌ Failed to create release")
                        console.print(Panel(f"[bold red]❌ Failed to create release: {response.status}[/]\n{error_text}", 
                                          title="[red]Error", border_style="red"))

    async def list_stats(self, repo_full_name: str):
        """Show repository stats: stars, forks, watchers, contributors"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Fetching stats for {repo_full_name}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                # Repo info
                url = f"{self.api_base}/repos/{repo_full_name}"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        repo = await response.json()
                        stars = repo.get('stargazers_count', 0)
                        forks = repo.get('forks_count', 0)
                        watchers = repo.get('subscribers_count', 0)
                    else:
                        progress.update(task, description="❌ Failed to fetch repo info")
                        console.print(Panel(f"[bold red]❌ Failed to fetch repo info: {response.status}[/]", 
                                          title="[red]Error", border_style="red"))
                        return
                # Contributors
                url = f"{self.api_base}/repos/{repo_full_name}/contributors"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        contributors = await response.json()
                        num_contributors = len(contributors)
                    else:
                        num_contributors = 'N/A'
                progress.update(task, description="✅ Stats fetched!")
                table = Table(title=f"[bold blue]Repository Stats for {repo_full_name}[/]", box=box.ROUNDED, border_style="blue")
                table.add_column("Metric", style="cyan", no_wrap=True)
                table.add_column("Value", style="green")
                table.add_row("Stars", str(stars))
                table.add_row("Forks", str(forks))
                table.add_row("Watchers", str(watchers))
                table.add_row("Contributors", str(num_contributors))
                console.print(table)

    async def list_branches_graph(self, repo_full_name: str):
        """Show a simple branch graph for the repository (based on recent commits and branches)"""
        if not self.auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first.[/]", 
                              title="[red]Error", border_style="red"))
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Fetching branches and commits for {repo_full_name}...", total=None)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.auth.get_access_token()}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                # Get branches
                url = f"{self.api_base}/repos/{repo_full_name}/branches"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        branches = await response.json()
                    else:
                        progress.update(task, description="❌ Failed to fetch branches")
                        console.print(Panel(f"[bold red]❌ Failed to fetch branches: {response.status}[/]", 
                                          title="[red]Error", border_style="red"))
                        return
                # Get recent commits for each branch (limit to 10 per branch)
                branch_commits = {}
                for branch in branches:
                    branch_name = branch['name']
                    url = f"{self.api_base}/repos/{repo_full_name}/commits"
                    params = {'sha': branch_name, 'per_page': 10}
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            commits = await response.json()
                            branch_commits[branch_name] = commits
                        else:
                            branch_commits[branch_name] = []
                progress.update(task, description="✅ Branches and commits fetched!")
                # Render a simple graph (just show branch names and their latest commit SHAs)
                from rich.tree import Tree
                tree = Tree(f"[bold blue]Branches in {repo_full_name}[/]")
                for branch, commits in branch_commits.items():
                    branch_node = tree.add(f"[green]{branch}[/]")
                    for commit in commits:
                        sha = commit.get('sha', '')[:7]
                        msg = commit.get('commit', {}).get('message', '').split('\n')[0][:40]
                        branch_node.add(f"[cyan]{sha}[/] [dim]{msg}[/]")
                console.print(tree) 