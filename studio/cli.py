#!/usr/bin/env python3
"""
CLI interface for gitflow-studio
Provides comprehensive Git workflow management through command line
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.columns import Columns
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.syntax import Syntax
from rich.tree import Tree
from rich.rule import Rule
from datetime import datetime
import subprocess

from studio.git.git_operations import GitOperations
from studio.core.app_context import AppContext
from studio.core.plugin_loader import PluginLoader

console = Console()

# ASCII Art Banner
BANNER = """
[bold cyan]
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██████╗ ██╗████████╗███████╗██╗     ██╗      ██████╗ ██╗    ██╗          ║
║  ██╔════╝ ██║╚══██╔══╝██╔════╝██║     ██║     ██╔═══██╗██║    ██║          ║
║  ██║  ███╗██║   ██║   █████╗  ██║     ██║     ██║   ██║██║ █╗ ██║          ║
║  ██║   ██║██║   ██║   ██╔══╝  ██║     ██║     ██║   ██║██║███╗██║          ║
║  ╚██████╔╝██║   ██║   ███████╗███████╗███████╗╚██████╔╝╚███╔███╔╝          ║
║   ╚═════╝ ╚═╝   ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝  ╚══╝╚══╝           ║
║                                                                              ║
║                    [bold yellow]Comprehensive Git Workflow Management[/]                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
[/bold cyan]
"""

class GitFlowStudioCLI:
    def __init__(self):
        self.app_context = AppContext()
        self.git_ops = None
        self.current_repo = None
        
    def show_banner(self):
        """Display the ASCII art banner"""
        console.print(BANNER)
        console.print(f"[dim]Version 1.0.0 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n")
        
    async def initialize(self):
        """Initialize with progress indicator"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing GitFlow Studio...", total=None)
            await self.app_context.initialize()
            progress.update(task, description="✅ GitFlow Studio initialized successfully!")
            
    def discover_repositories(self, start_path: str = ".") -> List[str]:
        """Discover Git repositories in the given path"""
        repos = []
        start_path_obj = Path(start_path).resolve()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Discovering Git repositories...", total=None)
            
            for root, dirs, files in os.walk(start_path_obj):
                if '.git' in dirs:
                    repo_path = Path(root)
                    repos.append(str(repo_path))
                    # Don't search inside .git directories
                    dirs[:] = [d for d in dirs if d != '.git']
                    
            progress.update(task, description=f"✅ Found {len(repos)} repositories!")
            
        return repos
        
    def show_repository_discovery(self, start_path: str = "."):
        """Show discovered repositories in a nice format"""
        repos = self.discover_repositories(start_path)
        
        if not repos:
            console.print(Panel("[yellow]No Git repositories found in the specified path.[/]", 
                              title="[blue]Repository Discovery", border_style="blue"))
            return []
            
        table = Table(
            title=f"[bold blue]Discovered Git Repositories[/]\n[dim]Found {len(repos)} repositories[/]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="blue"
        )
        table.add_column("#", style="cyan", no_wrap=True)
        table.add_column("Repository Path", style="white")
        table.add_column("Name", style="green")
        
        for i, repo_path in enumerate(repos, 1):
            repo_name = Path(repo_path).name
            table.add_row(
                f"[bold]{i}[/]",
                repo_path,
                f"[bold green]{repo_name}[/]"
            )
            
        console.print(table)
        return repos
        
    def interactive_mode(self):
        """Run in interactive mode"""
        console.print(Panel("[bold blue]Welcome to GitFlow Studio Interactive Mode![/]\n[dim]Type 'help' for available commands or 'exit' to quit.[/]", 
                          title="[green]Interactive Mode", border_style="green"))
        
        while True:
            try:
                command = Prompt.ask("\n[bold cyan]gitflow-studio>[/]")
                
                if command.lower() in ['exit', 'quit', 'q']:
                    console.print("[yellow]Goodbye! 👋[/]")
                    break
                elif command.lower() in ['help', 'h', '?']:
                    self.show_interactive_help()
                elif command.lower() == 'discover':
                    repos = self.show_repository_discovery()
                    if repos:
                        choice = Prompt.ask("\n[bold]Select repository number to open[/]", default="1")
                        try:
                            repo_index = int(choice) - 1
                            if 0 <= repo_index < len(repos):
                                self.set_repository(repos[repo_index])
                            else:
                                console.print("[red]Invalid repository number![/]")
                        except ValueError:
                            console.print("[red]Please enter a valid number![/]")
                elif command.lower() == 'status':
                    asyncio.run(self.status())
                elif command.lower() == 'log':
                    count = Prompt.ask("Number of commits", default="10")
                    asyncio.run(self.log(int(count)))
                elif command.lower() == 'branches':
                    asyncio.run(self.branches())
                elif command.lower() == 'stash list':
                    asyncio.run(self.stash_list())
                elif command.lower().startswith('commit '):
                    message = command[7:]
                    add_all = Confirm.ask("Add all changes before commit?")
                    asyncio.run(self.commit(message, add_all))
                elif command.lower().startswith('checkout '):
                    ref = command[9:]
                    asyncio.run(self.checkout(ref))
                elif command.lower().startswith('branch create '):
                    name = command[14:]
                    start_point = Prompt.ask("Start point (optional)", default="")
                    start_point = start_point if start_point else None
                    asyncio.run(self.create_branch(name, start_point))
                elif command.lower() == 'stash':
                    message = Prompt.ask("Stash message (optional)", default="")
                    message = message if message else None
                    asyncio.run(self.stash(message))
                elif command.lower() == 'stash pop':
                    asyncio.run(self.stash_pop())
                elif command.lower() == 'push':
                    asyncio.run(self.push())
                elif command.lower() == 'pull':
                    asyncio.run(self.pull())
                elif command.lower() == 'gitflow init':
                    asyncio.run(self.gitflow_init())
                elif command.lower().startswith('gitflow feature start '):
                    name = command[23:]
                    asyncio.run(self.gitflow_feature_start(name))
                elif command.lower().startswith('gitflow feature finish '):
                    name = command[24:]
                    asyncio.run(self.gitflow_feature_finish(name))
                elif command.lower().startswith('gitflow release start '):
                    version = command[23:]
                    asyncio.run(self.gitflow_release_start(version))
                elif command.lower().startswith('gitflow release finish '):
                    version = command[24:]
                    asyncio.run(self.gitflow_release_finish(version))
                elif command.lower() == 'repo info':
                    self.show_repository_info()
                elif command.lower() == 'clear':
                    console.clear()
                    self.show_banner()
                else:
                    console.print(f"[red]Unknown command: {command}[/]")
                    console.print("[dim]Type 'help' for available commands.[/]")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit or 'help' for commands.[/]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/]")
                
    def show_interactive_help(self):
        """Show help for interactive mode"""
        help_text = """
[bold blue]Available Commands:[/]

[bold green]Repository Management:[/]
  discover          - Discover Git repositories in current directory
  repo info         - Show current repository information

[bold green]Git Operations:[/]
  status            - Show repository status
  log [count]       - Show commit log (default: 10 commits)
  branches          - List all branches
  checkout <ref>    - Checkout branch or commit
  branch create <name> - Create new branch
  commit <message>  - Create commit with message
  push              - Push changes to remote
  pull              - Pull changes from remote

[bold green]Stash Operations:[/]
  stash [message]   - Create stash (optional message)
  stash list        - List all stashes
  stash pop         - Pop latest stash

[bold green]Git Flow Operations:[/]
  gitflow init      - Initialize Git Flow
  gitflow feature start <name>  - Start feature branch
  gitflow feature finish <name> - Finish feature branch
  gitflow release start <version> - Start release branch
  gitflow release finish <version> - Finish release branch

[bold green]System:[/]
  help              - Show this help
  clear             - Clear screen
  exit/quit/q       - Exit interactive mode

[dim]Examples:[/]
  checkout main
  branch create feature/new-feature
  commit "Add new feature"
  gitflow feature start my-feature
        """
        console.print(Panel(help_text, title="[blue]Interactive Mode Help", border_style="blue"))
        
    def show_repository_info(self):
        """Show detailed repository information"""
        if not self.current_repo:
            console.print(Panel("[bold red]❌ No repository selected.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            # Get additional repository info
            repo_path = Path(self.current_repo)
            
            # Get remote info
            try:
                result = subprocess.run(['git', '-C', self.current_repo, 'remote', '-v'], 
                                      capture_output=True, text=True, timeout=5)
                remotes = result.stdout.strip()
            except:
                remotes = "No remotes configured"
                
            # Get current branch
            try:
                result = subprocess.run(['git', '-C', self.current_repo, 'branch', '--show-current'], 
                                      capture_output=True, text=True, timeout=5)
                current_branch = result.stdout.strip()
            except:
                current_branch = "Unknown"
                
            info = f"""
[bold blue]Repository Information[/]

[bright_blue]Path:[/] {self.current_repo}
[bright_blue]Name:[/] {repo_path.name}
[bright_blue]Current Branch:[/] [green]{current_branch}[/]
[bright_blue]Size:[/] {self.get_directory_size(repo_path)} MB
[bright_blue]Last Modified:[/] {datetime.fromtimestamp(repo_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}

[bold blue]Remote Configuration:[/]
{remotes}
            """
            
            console.print(Panel(info, title="[green]Repository Info", border_style="green"))
            
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error getting repository info:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    def get_directory_size(self, path: Path) -> float:
        """Get directory size in MB"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except:
            pass
        return round(total_size / (1024 * 1024), 2)
        
    def set_repository(self, repo_path: str):
        """Set the current repository with enhanced feedback"""
        if not os.path.exists(repo_path):
            console.print(Panel(f"[bold red]❌ Repository path does not exist:[/] {repo_path}", 
                              title="[red]Error", border_style="red"))
            return False
            
        try:
            self.current_repo = repo_path
            self.git_ops = GitOperations(repo_path)
            
            # Create a nice panel for repository info
            repo_info = f"""
[bold green]✅ Repository Set Successfully![/]

[bright_blue]Path:[/] {repo_path}
[bright_blue]Type:[/] Git Repository
[bright_blue]Status:[/] [green]Ready[/]
            """
            console.print(Panel(repo_info, title="[green]Repository Info", border_style="green"))
            return True
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Failed to set repository:[/] {e}", 
                              title="[red]Error", border_style="red"))
            return False
            
    async def status(self):
        """Show repository status with enhanced formatting"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            status = await self.git_ops.status()
            
            # Create status summary
            status_lines = status.splitlines() if status.strip() else []
            staged_count = len([l for l in status_lines if l.startswith('A') or l.startswith('M')])
            modified_count = len([l for l in status_lines if l.startswith(' M')])
            untracked_count = len([l for l in status_lines if l.startswith('??')])
            
            summary = f"""
[bold blue]Repository Status Summary[/]

[green]Staged Changes:[/] {staged_count}
[cyan]Modified Files:[/] {modified_count}
[yellow]Untracked Files:[/] {untracked_count}
[blue]Total Changes:[/] {len(status_lines)}
            """
            
            console.print(Panel(summary, title="[blue]Status Summary", border_style="blue"))
            
            if not status.strip():
                console.print(Panel("[green]✔️ Working directory clean![/]", 
                                  title="[green]Clean Status", border_style="green"))
            else:
                console.rule("[bold blue]Detailed Status")
                for line in status_lines:
                    if line.startswith('A'):
                        console.print(f"[yellow]📁 Added:[/] {line[3:]}", style="yellow")
                    elif line.startswith('M'):
                        console.print(f"[cyan]📝 Modified:[/] {line[3:]}", style="cyan")
                    elif line.startswith('D'):
                        console.print(f"[red]🗑️ Deleted:[/] {line[3:]}", style="red")
                    elif line.startswith('??'):
                        console.print(f"[bright_black]❓ Untracked:[/] {line[3:]}", style="bright_black")
                    else:
                        console.print(line)
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error getting status:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def log(self, max_count: int = 20):
        """Show commit log with enhanced formatting"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            log = await self.git_ops.log(max_count=max_count)
            
            console.print(Panel(f"[bold blue]Commit History[/]\n[dim]Showing last {max_count} commits[/]", 
                              title="[blue]Git Log", border_style="blue"))
            
            for line in log.splitlines():
                if line.startswith('*'):
                    # Parse commit hash and message
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        hash_part = parts[1]
                        message = parts[2]
                        console.print(f"[bold green]●[/] [cyan]{hash_part}[/] [white]{message}[/]")
                    else:
                        console.print(f"[bold green]{line}[/]")
                else:
                    console.print(line, style="dim")
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error getting log:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def branches(self):
        """List all branches with enhanced table"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            branches = await self.git_ops.branches()
            
            table = Table(
                title="[bold blue]Branch Information",
                show_header=True,
                header_style="bold magenta",
                box=box.ROUNDED,
                border_style="blue"
            )
            table.add_column("Branch", style="cyan", no_wrap=True)
            table.add_column("Status", style="green")
            table.add_column("Type", style="yellow")
            
            for line in branches.splitlines():
                if line.startswith('*'):
                    table.add_row(
                        f"[bold green]{line[2:]}[/]",
                        "[green]● Current[/]",
                        "[yellow]Local[/]"
                    )
                else:
                    table.add_row(
                        line.strip(),
                        "",
                        "[yellow]Local[/]"
                    )
            
            console.print(table)
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error getting branches:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def create_branch(self, name: str, start_point: Optional[str] = None):
        """Create a new branch with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Creating branch '{name}'...", total=None)
                await self.git_ops.create_branch(name, start_point)
                progress.update(task, description=f"✅ Branch '{name}' created successfully!")
            
            console.print(Panel(f"[bold green]✅ Branch '{name}' created successfully![/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error creating branch:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def checkout(self, ref: str):
        """Checkout a branch with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Switching to '{ref}'...", total=None)
                await self.git_ops.checkout(ref)
                progress.update(task, description=f"✅ Switched to '{ref}' successfully!")
            
            console.print(Panel(f"[bold green]✅ Switched to '{ref}'[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error checking out:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def merge(self, branch: str):
        """Merge a branch with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Merging '{branch}'...", total=None)
                await self.git_ops.merge(branch)
                progress.update(task, description=f"✅ Merged '{branch}' successfully!")
            
            console.print(Panel(f"[bold green]✅ Merged '{branch}' successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error merging:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def rebase(self, branch: str):
        """Rebase current branch with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Rebasing onto '{branch}'...", total=None)
                await self.git_ops.rebase(branch)
                progress.update(task, description=f"✅ Rebased onto '{branch}' successfully!")
            
            console.print(Panel(f"[bold green]✅ Rebased onto '{branch}' successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error rebasing:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def stash(self, message: Optional[str] = None):
        """Create a stash with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Creating stash...", total=None)
                await self.git_ops.stash(message)
                progress.update(task, description="✅ Stash created successfully!")
            
            console.print(Panel("[bold green]✅ Stash created successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error creating stash:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def stash_list(self):
        """List stashes with enhanced formatting"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            stashes = await self.git_ops.stash_list()
            
            if not stashes.strip():
                console.print(Panel("[green]No stashes found.[/]", 
                                  title="[blue]Stash List", border_style="blue"))
            else:
                table = Table(
                    title="[bold blue]Stash List",
                    show_header=True,
                    header_style="bold magenta",
                    box=box.ROUNDED,
                    border_style="blue"
                )
                table.add_column("Stash", style="cyan", no_wrap=True)
                table.add_column("Message", style="white")
                
                for line in stashes.splitlines():
                    if line.strip():
                        parts = line.split(':', 1)
                        if len(parts) >= 2:
                            stash_ref = parts[0]
                            message = parts[1].strip()
                            table.add_row(f"[yellow]{stash_ref}[/]", message)
                        else:
                            table.add_row(line, "")
                
                console.print(table)
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error listing stashes:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def stash_pop(self, stash_ref: str = "stash@{0}"):
        """Pop a stash with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Popping stash '{stash_ref}'...", total=None)
                await self.git_ops.stash_pop(stash_ref)
                progress.update(task, description=f"✅ Stash '{stash_ref}' popped successfully!")
            
            console.print(Panel(f"[bold green]✅ Stash '{stash_ref}' popped successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error popping stash:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def commit(self, message: str, add_all: bool = False):
        """Create a commit with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Creating commit...", total=None)
                await self.git_ops.commit(message, add_all=add_all)
                progress.update(task, description="✅ Commit created successfully!")
            
            console.print(Panel(f"[bold green]✅ Commit created successfully[/]\n[dim]Message:[/] {message}", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error creating commit:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def push(self, remote: Optional[str] = None, branch: Optional[str] = None):
        """Push changes with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Pushing changes...", total=None)
                await self.git_ops.push(remote, branch)
                progress.update(task, description="✅ Changes pushed successfully!")
            
            console.print(Panel("[bold green]✅ Changes pushed successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error pushing:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def pull(self, remote: Optional[str] = None, branch: Optional[str] = None):
        """Pull changes with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Pulling changes...", total=None)
                await self.git_ops.pull(remote, branch)
                progress.update(task, description="✅ Changes pulled successfully!")
            
            console.print(Panel("[bold green]✅ Changes pulled successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error pulling:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def gitflow_init(self):
        """Initialize Git Flow with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Initializing Git Flow...", total=None)
                await self.git_ops.gitflow_init()
                progress.update(task, description="✅ Git Flow initialized successfully!")
            
            console.print(Panel("[bold green]✅ Git Flow initialized successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error initializing Git Flow:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def gitflow_feature_start(self, name: str):
        """Start a feature branch with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Starting feature '{name}'...", total=None)
                await self.git_ops.gitflow_feature_start(name)
                progress.update(task, description=f"✅ Feature '{name}' started successfully!")
            
            console.print(Panel(f"[bold green]✅ Feature branch '{name}' started successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error starting feature:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def gitflow_feature_finish(self, name: str):
        """Finish a feature branch with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Finishing feature '{name}'...", total=None)
                await self.git_ops.gitflow_feature_finish(name)
                progress.update(task, description=f"✅ Feature '{name}' finished successfully!")
            
            console.print(Panel(f"[bold green]✅ Feature branch '{name}' finished successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error finishing feature:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def gitflow_release_start(self, version: str):
        """Start a release branch with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Starting release '{version}'...", total=None)
                await self.git_ops.gitflow_release_start(version)
                progress.update(task, description=f"✅ Release '{version}' started successfully!")
            
            console.print(Panel(f"[bold green]✅ Release branch '{version}' started successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error starting release:[/] {e}", 
                              title="[red]Error", border_style="red"))
            
    async def gitflow_release_finish(self, version: str):
        """Finish a release branch with progress indicator"""
        if not self.git_ops:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Finishing release '{version}'...", total=None)
                await self.git_ops.gitflow_release_finish(version)
                progress.update(task, description=f"✅ Release '{version}' finished successfully!")
            
            console.print(Panel(f"[bold green]✅ Release branch '{version}' finished successfully[/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error finishing release:[/] {e}", 
                              title="[red]Error", border_style="red"))

def main():
    """Main CLI entry point"""
    cli = GitFlowStudioCLI()
    cli.show_banner()
    
    parser = argparse.ArgumentParser(
        description="[bold cyan]GitFlow Studio CLI[/] - [yellow]Comprehensive Git workflow management[/]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
[bold]Examples:[/]
  [green]gitflow-studio --repo /path/to/repo status[/]
  [green]gitflow-studio --repo /path/to/repo log --max-count 10[/]
  [green]gitflow-studio --repo /path/to/repo branch create feature/new-feature[/]
  [green]gitflow-studio --repo /path/to/repo gitflow init[/]
  [green]gitflow-studio --repo /path/to/repo gitflow feature start my-feature[/]
  [green]gitflow-studio --interactive[/]
        """
    )
    
    parser.add_argument('--repo', help='Repository path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--discover', action='store_true', help='Discover Git repositories in current directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show repository status')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Show commit log')
    log_parser.add_argument('--max-count', type=int, default=20, help='Maximum number of commits')
    
    # Branch commands
    branch_parser = subparsers.add_parser('branch', help='Branch operations')
    branch_subparsers = branch_parser.add_subparsers(dest='branch_command')
    
    branch_subparsers.add_parser('list', help='List all branches')
    
    create_branch_parser = branch_subparsers.add_parser('create', help='Create a new branch')
    create_branch_parser.add_argument('name', help='Branch name')
    create_branch_parser.add_argument('--start-point', help='Start point (branch/commit)')
    
    checkout_parser = branch_subparsers.add_parser('checkout', help='Checkout a branch')
    checkout_parser.add_argument('ref', help='Branch or commit to checkout')
    
    merge_parser = branch_subparsers.add_parser('merge', help='Merge a branch')
    merge_parser.add_argument('branch', help='Branch to merge')
    
    rebase_parser = branch_subparsers.add_parser('rebase', help='Rebase current branch')
    rebase_parser.add_argument('branch', help='Branch to rebase onto')
    
    # Stash commands
    stash_parser = subparsers.add_parser('stash', help='Stash operations')
    stash_subparsers = stash_parser.add_subparsers(dest='stash_command')
    
    stash_subparsers.add_parser('list', help='List stashes')
    
    create_stash_parser = stash_subparsers.add_parser('create', help='Create a stash')
    create_stash_parser.add_argument('--message', help='Stash message')
    
    pop_stash_parser = stash_subparsers.add_parser('pop', help='Pop a stash')
    pop_stash_parser.add_argument('--ref', default='stash@{0}', help='Stash reference')
    
    # Commit command
    commit_parser = subparsers.add_parser('commit', help='Create a commit')
    commit_parser.add_argument('message', help='Commit message')
    commit_parser.add_argument('--add-all', action='store_true', help='Add all changes before commit')
    
    # Push/Pull commands
    push_parser = subparsers.add_parser('push', help='Push changes')
    push_parser.add_argument('--remote', help='Remote name')
    push_parser.add_argument('--branch', help='Branch name')
    
    pull_parser = subparsers.add_parser('pull', help='Pull changes')
    pull_parser.add_argument('--remote', help='Remote name')
    pull_parser.add_argument('--branch', help='Branch name')
    
    # Git Flow commands
    gitflow_parser = subparsers.add_parser('gitflow', help='Git Flow operations')
    gitflow_subparsers = gitflow_parser.add_subparsers(dest='gitflow_command')
    
    gitflow_subparsers.add_parser('init', help='Initialize Git Flow')
    
    feature_start_parser = gitflow_subparsers.add_parser('feature-start', help='Start a feature branch')
    feature_start_parser.add_argument('name', help='Feature name')
    
    feature_finish_parser = gitflow_subparsers.add_parser('feature-finish', help='Finish a feature branch')
    feature_finish_parser.add_argument('name', help='Feature name')
    
    release_start_parser = gitflow_subparsers.add_parser('release-start', help='Start a release branch')
    release_start_parser.add_argument('version', help='Release version')
    
    release_finish_parser = gitflow_subparsers.add_parser('release-finish', help='Finish a release branch')
    release_finish_parser.add_argument('version', help='Release version')
    
    args = parser.parse_args()
    
    # Handle special modes
    if args.interactive:
        async def run_interactive():
            await cli.initialize()
            cli.interactive_mode()
        asyncio.run(run_interactive())
        return
        
    if args.discover:
        cli.show_repository_discovery()
        return
        
    if not args.command:
        parser.print_help()
        return
        
    if not args.repo:
        console.print(Panel("[bold red]❌ Repository path is required. Use --repo <path>[/]", 
                          title="[red]Error", border_style="red"))
        return
        
    async def run():
        await cli.initialize()
        
        if not cli.set_repository(args.repo):
            return
            
        # Execute commands
        if args.command == 'status':
            await cli.status()
        elif args.command == 'log':
            await cli.log(args.max_count)
        elif args.command == 'branch':
            if args.branch_command == 'list':
                await cli.branches()
            elif args.branch_command == 'create':
                await cli.create_branch(args.name, args.start_point)
            elif args.branch_command == 'checkout':
                await cli.checkout(args.ref)
            elif args.branch_command == 'merge':
                await cli.merge(args.branch)
            elif args.branch_command == 'rebase':
                await cli.rebase(args.branch)
        elif args.command == 'stash':
            if args.stash_command == 'list':
                await cli.stash_list()
            elif args.stash_command == 'create':
                await cli.stash(args.message)
            elif args.stash_command == 'pop':
                await cli.stash_pop(args.ref)
        elif args.command == 'commit':
            await cli.commit(args.message, args.add_all)
        elif args.command == 'push':
            await cli.push(args.remote, args.branch)
        elif args.command == 'pull':
            await cli.pull(args.remote, args.branch)
        elif args.command == 'gitflow':
            if args.gitflow_command == 'init':
                await cli.gitflow_init()
            elif args.gitflow_command == 'feature-start':
                await cli.gitflow_feature_start(args.name)
            elif args.gitflow_command == 'feature-finish':
                await cli.gitflow_feature_finish(args.name)
            elif args.gitflow_command == 'release-start':
                await cli.gitflow_release_start(args.version)
            elif args.gitflow_command == 'release-finish':
                await cli.gitflow_release_finish(args.version)
    
    asyncio.run(run())

if __name__ == "__main__":
    main() 