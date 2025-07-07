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
from studio.github.auth import GitHubAuth
from studio.github.repos import GitHubRepos

console = Console()

# ASCII Art Banner
BANNER = """
[bold cyan]
╔════════════════════════════════════════════════════════╗
║                                                      ║
║   ████████████████████████████████████████████████   ║
║   ████████████████████████████████████████████████   ║
║   ████████████████████████████████████████████████   ║
║                                                      ║
╚════════════════════════════════════════════════════════╝
                By Sherin Joseph Roy
[/bold cyan]
"""

class GitFlowStudioCLI:
    def __init__(self):
        self.app_context = AppContext()
        self.git_ops = None
        self.current_repo = None
        self.github_auth = GitHubAuth()
        self.github_repos = GitHubRepos(self.github_auth)
        
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
        
    async def interactive_mode(self):
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
                    start_point = Prompt.ask("Start point (optional)", default="") or None
                    asyncio.run(self.create_branch(name, start_point))
                elif command.lower().startswith('branch delete '):
                    repo = self.current_repo
                    if not repo:
                        console.print("[red]No repository selected![/]")
                    else:
                        if not self.git_ops:
                            self.git_ops = GitOperations(repo)
                        parts = command.split()
                        name = parts[2] if len(parts) > 2 else Prompt.ask("Branch name to delete")
                        force = Confirm.ask("Force delete (even if not merged)?", default=False)
                        result = asyncio.run(self.git_ops.delete_branch(name, force))
                        print(result)
                elif command.lower().startswith('branch delete-remote '):
                    repo = self.current_repo
                    if not repo:
                        console.print("[red]No repository selected![/]")
                    else:
                        if not self.git_ops:
                            self.git_ops = GitOperations(repo)
                        parts = command.split()
                        name = parts[2] if len(parts) > 2 else Prompt.ask("Remote branch name to delete")
                        remote = Prompt.ask("Remote name", default="origin")
                        result = asyncio.run(self.git_ops.delete_remote_branch(name, remote))
                        print(result)
                elif command.lower().startswith('branch rename '):
                    repo = self.current_repo
                    if not repo:
                        console.print("[red]No repository selected![/]")
                    else:
                        if not self.git_ops:
                            self.git_ops = GitOperations(repo)
                        parts = command.split()
                        if len(parts) >= 4:
                            old_name = parts[2]
                            new_name = parts[3]
                        else:
                            old_name = Prompt.ask("Current branch name")
                            new_name = Prompt.ask("New branch name")
                        result = asyncio.run(self.git_ops.rename_branch(old_name, new_name))
                        print(result)
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
                elif command.lower() == 'github login':
                    asyncio.run(self.github_login())
                elif command.lower() == 'github logout':
                    self.github_logout()
                elif command.lower() == 'github repos':
                    await self.github_list_repos()
                elif command.lower().startswith('github clone '):
                    repo_name = command[13:]
                    await self.github_clone_repo(repo_name)
                elif command.lower().startswith('github search '):
                    query = command[14:]
                    await self.github_search_repos(query)
                elif command.lower() == 'clear':
                    console.clear()
                    self.show_banner()
                elif command.lower().startswith('github issues '):
                    self.github_issues_mode(command)
                elif command.lower().startswith('github prs '):
                    self.github_prs_mode(command)
                elif command.lower().startswith('github notifications '):
                    self.github_notifications_mode(command)
                elif command.lower().startswith('github releases '):
                    self.github_releases_mode(command)
                elif command.lower() == 'github stats':
                    self.github_stats_mode(command)
                elif command.lower().startswith('github branches '):
                    self.github_branches_mode(command)
                elif command.lower().startswith('tag list'):
                    repo = self.current_repo
                    if not repo:
                        console.print("[red]No repository selected![/]")
                    else:
                        if not self.git_ops:
                            self.git_ops = GitOperations(repo)
                        result = asyncio.run(self.git_ops.list_tags())
                        print(result)
                elif command.lower().startswith('tag create '):
                    repo = self.current_repo
                    if not repo:
                        console.print("[red]No repository selected![/]")
                    else:
                        if not self.git_ops:
                            self.git_ops = GitOperations(repo)
                        parts = command.split()
                        name = parts[2] if len(parts) > 2 else Prompt.ask("Tag name")
                        annotated = Confirm.ask("Annotated tag?", default=False)
                        message = Prompt.ask("Tag message (optional)", default="") if annotated else None
                        commit = Prompt.ask("Commit hash (optional)", default="") or None
                        result = asyncio.run(self.git_ops.create_tag(name, message=message, annotated=annotated, commit=commit))
                        print(result)
                elif command.lower().startswith('tag delete '):
                    repo = self.current_repo
                    if not repo:
                        console.print("[red]No repository selected![/]")
                    else:
                        if not self.git_ops:
                            self.git_ops = GitOperations(repo)
                        parts = command.split()
                        name = parts[2] if len(parts) > 2 else Prompt.ask("Tag name to delete")
                        result = asyncio.run(self.git_ops.delete_tag(name))
                        print(result)
                elif command.lower().startswith('tag show '):
                    repo = self.current_repo
                    if not repo:
                        console.print("[red]No repository selected![/]")
                    else:
                        if not self.git_ops:
                            self.git_ops = GitOperations(repo)
                        parts = command.split()
                        name = parts[2] if len(parts) > 2 else Prompt.ask("Tag name to show")
                        result = asyncio.run(self.git_ops.show_tag_details(name))
                        print(result)
                elif command.lower().startswith('cherry-pick '):
                    repo = self.current_repo
                    if not repo:
                        console.print("[red]No repository selected![/]")
                    else:
                        if not self.git_ops:
                            self.git_ops = GitOperations(repo)
                        parts = command.split()
                        if len(parts) > 1:
                            commit = parts[1]
                        else:
                            commit = Prompt.ask("Commit hash to cherry-pick")
                        no_commit = Confirm.ask("No auto-commit?", default=False)
                        cmd = ['cherry-pick']
                        if no_commit:
                            cmd.append('--no-commit')
                        cmd.append(commit)
                        result = asyncio.run(self.git_ops._run_git_command(*cmd))
                        print(result)
                elif command.lower().startswith('revert '):
                    repo = self.current_repo
                    if not repo:
                        console.print("[red]No repository selected![/]")
                    else:
                        if not self.git_ops:
                            self.git_ops = GitOperations(repo)
                        parts = command.split()
                        if len(parts) > 1:
                            commit = parts[1]
                        else:
                            commit = Prompt.ask("Commit hash to revert")
                        no_commit = Confirm.ask("No auto-commit?", default=False)
                        cmd = ['revert']
                        if no_commit:
                            cmd.append('--no-commit')
                        cmd.append(commit)
                        result = asyncio.run(self.git_ops._run_git_command(*cmd))
                        print(result)
                elif command.lower().startswith('rebase-interactive '):
                    base = command[18:]
                    asyncio.run(self.rebase_interactive(base))
                elif command.lower().startswith('squash '):
                    num = int(command[7:])
                    message = Prompt.ask("Commit message for the squashed commit", default="")
                    asyncio.run(self.squash(num, message))
                elif command.lower().startswith('analytics '):
                    parts = command.split()
                    if len(parts) >= 2:
                        subcommand = parts[1]
                        repo = self.current_repo
                        if not repo:
                            console.print("[red]No repository selected![/]")
                        else:
                            if not self.git_ops:
                                self.git_ops = GitOperations(repo)
                            if subcommand == 'stats':
                                result = asyncio.run(self.git_ops.get_repository_stats())
                                asyncio.run(self.display_repository_stats(result))
                            elif subcommand == 'activity':
                                days = int(parts[2]) if len(parts) > 2 else 30
                                result = asyncio.run(self.git_ops.get_commit_activity(days))
                                asyncio.run(self.display_commit_activity(result, days))
                            elif subcommand == 'files':
                                days = int(parts[2]) if len(parts) > 2 else 30
                                result = asyncio.run(self.git_ops.get_file_changes(days))
                                asyncio.run(self.display_file_changes(result, days))
                            elif subcommand == 'branches':
                                result = asyncio.run(self.git_ops.get_branch_activity())
                                asyncio.run(self.display_branch_activity(result))
                            elif subcommand == 'contributors':
                                result = asyncio.run(self.git_ops.get_contributor_stats())
                                asyncio.run(self.display_contributor_stats(result))
                            elif subcommand == 'health':
                                result = asyncio.run(self.git_ops.get_repository_health())
                                asyncio.run(self.display_repository_health(result))
                            else:
                                console.print("[red]Unknown analytics command. Use: stats, activity, files, branches, contributors, health[/]")
                    else:
                        console.print("[red]Analytics command requires a subcommand. Use: stats, activity, files, branches, contributors, health[/]")
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
  branch delete <name> - Delete local branch
  branch delete-remote <name> - Delete remote branch
  branch rename <old> <new> - Rename branch
  commit <message>  - Create commit with message
  push              - Push changes to remote
  pull              - Pull changes from remote
  cherry-pick <hash> - Cherry-pick a commit
  revert <hash>     - Revert a commit

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

[bold green]GitHub Operations:[/]
  github login      - Login to GitHub
  github logout     - Logout from GitHub
  github repos      - List your GitHub repositories
  github clone <name> - Clone a repository by name
  github search <query> - Search GitHub repositories

[bold green]System:[/]
  help              - Show this help
  clear             - Clear screen
  exit/quit/q       - Exit interactive mode

[bold green]Tag Operations:[/]
  tag list           - List all tags
  tag create <name>  - Create a new tag
  tag delete <name>  - Delete a tag
  tag show <name>    - Show tag details

[bold green]Analytics & Statistics:[/]
  analytics stats    - Show comprehensive repository statistics
  analytics activity [days] - Show commit activity over time
  analytics files [days] - Show file change statistics
  analytics branches - Show branch activity and health
  analytics contributors - Show contributor statistics
  analytics health   - Show repository health indicators

[dim]Examples:[/]
  checkout main
  branch create feature/new-feature
  commit "Add new feature"
  gitflow feature start my-feature
  analytics stats
  analytics activity 30
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
    
    async def github_login(self):
        """Login to GitHub"""
        success = await self.github_auth.login()
        if success:
            console.print(Panel("[bold green]✅ GitHub login successful![/]", 
                              title="[green]Success", border_style="green"))
        else:
            console.print(Panel("[bold red]❌ GitHub login failed[/]", 
                              title="[red]Error", border_style="red"))
    
    def github_logout(self):
        """Logout from GitHub"""
        self.github_auth.logout()
    
    async def github_list_repos(self):
        """List GitHub repositories"""
        if not self.github_auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first with 'github login'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repos = await self.github_repos.list_repositories()
        self.github_repos.display_repositories(repos)
    
    async def github_clone_repo(self, repo_name: str):
        """Clone a GitHub repository"""
        if not self.github_auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first with 'github login'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        success = await self.github_repos.clone_repository(repo_name)
        if success:
            # Ask if user wants to set this as current repository
            if Confirm.ask("Set this as current repository?"):
                user_info = self.github_auth.get_user_info()
                if user_info:
                    repo_path = Path.home() / "git" / user_info['login'] / repo_name
                    if repo_path.exists():
                        self.set_repository(str(repo_path))
    
    async def github_search_repos(self, query: str):
        """Search GitHub repositories"""
        if not self.github_auth.is_authenticated():
            console.print(Panel("[bold red]❌ Not authenticated. Please login first with 'github login'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repos = await self.github_repos.search_repositories(query)
        self.github_repos.display_repositories(repos)

    def github_issues_mode(self, command: str):
        """Handle GitHub issues commands"""
        if not self.current_repo:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        command_parts = command.split(' ', 2)
        if len(command_parts) < 2:
            console.print(f"[red]Invalid command format. Use 'github issues <command> <args>'[/]")
            return
        
        command = command_parts[1]
        args = command_parts[2:] if len(command_parts) > 2 else []
        
        if command == 'list':
            self.github_issues_list_mode(args)
        elif command == 'create':
            self.github_issues_create_mode(args)
        else:
            console.print(f"[red]Unknown command: {command}[/]")

    def github_issues_list_mode(self, args: List[str]):
        """Handle 'github issues list' command"""
        if len(args) < 1:
            console.print(Panel("[bold red]❌ Repository is required. Use 'github issues list <repo>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo = args[0]
        asyncio.run(self.github_repos.list_issues(repo, 'open', 20))

    def github_issues_create_mode(self, args: List[str]):
        """Handle 'github issues create' command"""
        if len(args) < 2:
            console.print(Panel("[bold red]❌ Repository and title are required. Use 'github issues create <repo> <title>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo, title = args[0], args[1]
        body = args[2] if len(args) > 2 else ""
        asyncio.run(self.github_repos.create_issue(repo, title, body))

    def github_prs_mode(self, command: str):
        """Handle GitHub PRs commands"""
        if not self.current_repo:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        command_parts = command.split(' ', 2)
        if len(command_parts) < 2:
            console.print(f"[red]Invalid command format. Use 'github prs <command> <args>'[/]")
            return
        
        command = command_parts[1]
        args = command_parts[2:] if len(command_parts) > 2 else []
        
        if command == 'list':
            self.github_prs_list_mode(args)
        elif command == 'create':
            self.github_prs_create_mode(args)
        elif command == 'comment':
            self.github_prs_comment_mode(args)
        elif command == 'close':
            self.github_prs_close_mode(args)
        elif command == 'merge':
            self.github_prs_merge_mode(args)
        elif command == 'assign':
            self.github_prs_assign_mode(args)
        elif command == 'label':
            self.github_prs_label_mode(args)
        else:
            console.print(f"[red]Unknown command: {command}[/]")

    def github_prs_list_mode(self, args: List[str]):
        """Handle 'github prs list' command"""
        if len(args) < 1:
            console.print(Panel("[bold red]❌ Repository is required. Use 'github prs list <repo>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo = args[0]
        asyncio.run(self.github_repos.list_pull_requests(repo, 'open', 20))

    def github_prs_create_mode(self, args: List[str]):
        """Handle 'github prs create' command"""
        if len(args) < 2:
            console.print(Panel("[bold red]❌ Repository and title are required. Use 'github prs create <repo> <title>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo, title = args[0], args[1]
        body = args[2] if len(args) > 2 else ""
        asyncio.run(self.github_repos.create_pull_request(repo, title, body))

    def github_prs_comment_mode(self, args: List[str]):
        """Handle 'github prs comment' command"""
        if len(args) < 2:
            console.print(Panel("[bold red]❌ Repository and PR number are required. Use 'github prs comment <repo> <pr>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo, pr = args[0], args[1]
        body = args[2] if len(args) > 2 else ""
        asyncio.run(self.github_repos.comment_pull_request(repo, int(pr), body))

    def github_prs_close_mode(self, args: List[str]):
        """Handle 'github prs close' command"""
        if len(args) < 1:
            console.print(Panel("[bold red]❌ Repository is required. Use 'github prs close <repo>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo = args[0]
        asyncio.run(self.github_repos.close_pull_request(repo, int(args[0])))

    def github_prs_merge_mode(self, args: List[str]):
        """Handle 'github prs merge' command"""
        if len(args) < 1:
            console.print(Panel("[bold red]❌ Repository is required. Use 'github prs merge <repo>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo = args[0]
        asyncio.run(self.github_repos.merge_pull_request(repo, int(args[0]), args[1] if len(args) > 1 else 'merge'))

    def github_prs_assign_mode(self, args: List[str]):
        """Handle 'github prs assign' command"""
        if len(args) < 2:
            console.print(Panel("[bold red]❌ Repository and user are required. Use 'github prs assign <repo> <user>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo, user = args[0], args[1]
        result = asyncio.run(self.github_repos.assign_pull_request(repo, int(args[0]), args[1]))
        print(result)

    def github_prs_label_mode(self, args: List[str]):
        """Handle 'github prs label' command"""
        if len(args) < 2:
            console.print(Panel("[bold red]❌ Repository and label are required. Use 'github prs label <repo> <label>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo, label = args[0], args[1]
        result = asyncio.run(self.github_repos.label_pull_request(repo, int(args[0]), args[1]))
        print(result)

    def github_notifications_mode(self, command: str):
        """Handle GitHub notifications commands"""
        if not self.current_repo:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        command_parts = command.split(' ', 2)
        if len(command_parts) < 2:
            console.print(f"[red]Invalid command format. Use 'github notifications <command> <args>'[/]")
            return
        
        command = command_parts[1]
        args = command_parts[2:] if len(command_parts) > 2 else []
        
        if command == 'list':
            result = self.github_notifications_list_mode(args)
            print(result)
        elif command == 'mark-read':
            result = self.github_notifications_mark_read_mode(args)
            print(result)
        else:
            console.print(f"[red]Unknown command: {command}[/]")

    def github_notifications_list_mode(self, args: List[str]):
        """Handle 'github notifications list' command"""
        if len(args) < 1:
            console.print(Panel("[bold red]❌ Repository is required. Use 'github notifications list <repo>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo = args[0]
        result = asyncio.run(self.github_repos.list_notifications(all=args[0] == 'all'))
        print(result)

    def github_notifications_mark_read_mode(self, args: List[str]):
        """Handle 'github notifications mark-read' command"""
        if len(args) < 1:
            console.print(Panel("[bold red]❌ Repository is required. Use 'github notifications mark-read <repo>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo = args[0]
        result = asyncio.run(self.github_repos.mark_notifications_as_read(thread_id=args[0] or '', mark_all=args[0] == 'all'))
        print(result)

    def github_releases_mode(self, command: str):
        """Handle GitHub releases commands"""
        if not self.current_repo:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        command_parts = command.split(' ', 2)
        if len(command_parts) < 2:
            console.print(f"[red]Invalid command format. Use 'github releases <command> <args>'[/]")
            return
        
        command = command_parts[1]
        args = command_parts[2:] if len(command_parts) > 2 else []
        
        if command == 'list':
            self.github_releases_list_mode(args)
        elif command == 'create':
            self.github_releases_create_mode(args)
        else:
            console.print(f"[red]Unknown command: {command}[/]")

    async def github_releases_list_mode(self, args):
        await self.github_repos.list_releases(args.repo, args.limit)

    async def github_releases_create_mode(self, args):
        await self.github_repos.create_release(
            args.repo,
            args.tag,
            args.title,
            args.body or '',
            args.draft,
            args.prerelease
        )

    def github_stats_mode(self, command: str):
        """Handle GitHub stats commands"""
        if not self.current_repo:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        command_parts = command.split(' ', 2)
        if len(command_parts) < 2:
            console.print(f"[red]Invalid command format. Use 'github stats <command> <args>'[/]")
            return
        
        command = command_parts[1]
        args = command_parts[2:] if len(command_parts) > 2 else []
        
        if command == 'list':
            self.github_stats_list_mode(args)
        else:
            console.print(f"[red]Unknown command: {command}[/]")

    def github_stats_list_mode(self, args: List[str]):
        """Handle 'github stats list' command"""
        if len(args) < 1:
            console.print(Panel("[bold red]❌ Repository is required. Use 'github stats list <repo>'[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        repo = args[0]
        asyncio.run(self.github_repos.list_stats(repo))

    def github_branches_mode(self, command: str):
        """Handle GitHub branches commands"""
        if not self.current_repo:
            console.print(Panel("[bold red]❌ No repository selected. Use --repo <path> to set repository.[/]", 
                              title="[red]Error", border_style="red"))
            return
        
        command_parts = command.split(' ', 2)
        if len(command_parts) < 2:
            console.print(f"[red]Invalid command format. Use 'github branches <command> <args>'[/]")
            return
        
        command = command_parts[1]
        args = command_parts[2:] if len(command_parts) > 2 else []
        
        if command == 'graph':
            self.github_branches_graph_mode(args)
        else:
            console.print(f"[red]Unknown command: {command}[/]")

    async def github_branches_graph_mode(self, args):
        await self.github_repos.list_branches_graph(args.repo)

    async def rebase_interactive(self, base: str):
        """Interactive rebase onto a base branch or commit"""
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
                task = progress.add_task("Starting interactive rebase...", total=None)
                await self.git_ops.rebase_interactive(base)
                progress.update(task, description="✅ Interactive rebase started successfully!")
            
            console.print(Panel("[bold green]✅ Interactive rebase started successfully![/]", 
                              title="[green]Success", border_style="green"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ Error starting interactive rebase:[/] {e}", 
                              title="[red]Error", border_style="red"))

    async def squash(self, num: int, message: Optional[str] = None):
        """Squash last N commits into one"""
        if not self.current_repo:
            console.print(Panel("[bold red]❌ No repository selected![/]", 
                              title="[red]Error", border_style="red"))
            return
            
        if not self.git_ops:
            self.git_ops = GitOperations(self.current_repo)
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Squashing commits...", total=None)
            result = await self.git_ops.squash(num, message)
            progress.update(task, description="✅ Commits squashed successfully!")
            
        console.print(Panel(f"[green]{result}[/]", title="[blue]Squash Result", border_style="blue"))

    # Analytics Display Methods
    def display_repository_stats(self, stats):
        """Display comprehensive repository statistics"""
        if 'error' in stats:
            console.print(Panel(f"[red]Error: {stats['error']}[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        # Create main stats panel
        stats_table = Table(title="[bold blue]Repository Statistics[/]", 
                           show_header=True, header_style="bold magenta", box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan", no_wrap=True)
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Total Commits", f"[bold green]{stats.get('total_commits', 0)}[/]")
        stats_table.add_row("Total Branches", f"[bold green]{stats.get('total_branches', 0)}[/]")
        stats_table.add_row("Total Tags", f"[bold green]{stats.get('total_tags', 0)}[/]")
        stats_table.add_row("Total Files", f"[bold green]{stats.get('total_files', 0)}[/]")
        stats_table.add_row("Contributors", f"[bold green]{stats.get('contributors', 0)}[/]")
        stats_table.add_row("Recent Commits (30d)", f"[bold green]{stats.get('recent_commits', 0)}[/]")
        stats_table.add_row("Current Branch", f"[bold yellow]{stats.get('current_branch', 'Unknown')}[/]")
        
        console.print(stats_table)
        
        # Repository size info
        if 'repo_size' in stats:
            console.print(Panel(f"[cyan]Repository Size:[/]\n{stats['repo_size']}", 
                              title="[blue]Size Information", border_style="blue"))
        
        # Last commit info
        if 'last_commit' in stats:
            last_commit = stats['last_commit']
            commit_info = f"""
[bold]Hash:[/] {last_commit['hash']}
[bold]Author:[/] {last_commit['author']} ({last_commit['email']})
[bold]Date:[/] {last_commit['date']}
[bold]Message:[/] {last_commit['message']}
"""
            console.print(Panel(commit_info, title="[blue]Last Commit", border_style="blue"))

    def display_commit_activity(self, activity, days):
        """Display commit activity over time"""
        if 'error' in activity:
            console.print(Panel(f"[red]Error: {activity['error']}[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        if not activity:
            console.print(Panel("[yellow]No commit activity found in the specified period.[/]", 
                              title="[yellow]No Activity", border_style="yellow"))
            return
            
        # Create activity table
        activity_table = Table(title=f"[bold blue]Commit Activity (Last {days} Days)[/]", 
                              show_header=True, header_style="bold magenta", box=box.ROUNDED)
        activity_table.add_column("Date", style="cyan", no_wrap=True)
        activity_table.add_column("Commits", style="white", justify="center")
        
        # Sort by date
        sorted_activity = sorted(activity.items(), key=lambda x: x[0])
        for date, count in sorted_activity:
            activity_table.add_row(date, f"[bold green]{count}[/]")
            
        console.print(activity_table)
        
        # Summary
        total_commits = sum(activity.values())
        avg_per_day = total_commits / len(activity) if activity else 0
        console.print(Panel(f"[cyan]Total Commits:[/] {total_commits}\n[cyan]Average per Day:[/] {avg_per_day:.1f}", 
                          title="[blue]Summary", border_style="blue"))

    def display_file_changes(self, changes, days):
        """Display file change statistics"""
        if 'error' in changes:
            console.print(Panel(f"[red]Error: {changes['error']}[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        # Most changed files
        if 'most_changed_files' in changes:
            files_table = Table(title=f"[bold blue]Most Changed Files (Last {days} Days)[/]", 
                               show_header=True, header_style="bold magenta", box=box.ROUNDED)
            files_table.add_column("File", style="cyan")
            files_table.add_column("Changes", style="white", justify="center")
            
            for file_path, count in list(changes['most_changed_files'].items())[:10]:
                files_table.add_row(file_path, f"[bold green]{count}[/]")
                
            console.print(files_table)
        
        # File types
        if 'file_types' in changes:
            types_table = Table(title="[bold blue]Changes by File Type[/]", 
                               show_header=True, header_style="bold magenta", box=box.ROUNDED)
            types_table.add_column("Extension", style="cyan")
            types_table.add_column("Count", style="white", justify="center")
            
            for ext, count in sorted(changes['file_types'].items(), key=lambda x: x[1], reverse=True):
                types_table.add_row(ext or "No extension", f"[bold green]{count}[/]")
                
            console.print(types_table)
        
        # Summary
        total_files = changes.get('total_files_changed', 0)
        console.print(Panel(f"[cyan]Total Files Changed:[/] {total_files}", 
                          title="[blue]Summary", border_style="blue"))

    def display_branch_activity(self, activity):
        """Display branch activity and health"""
        if 'error' in activity:
            console.print(Panel(f"[red]Error: {activity['error']}[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        # Branch information
        if 'branches' in activity:
            branches_table = Table(title="[bold blue]Branch Activity[/]", 
                                  show_header=True, header_style="bold magenta", box=box.ROUNDED)
            branches_table.add_column("Branch", style="cyan")
            branches_table.add_column("Last Commit Date", style="white")
            branches_table.add_column("Last Commit Message", style="green")
            
            for branch in activity['branches'][:10]:  # Show top 10
                branches_table.add_row(
                    branch['name'],
                    branch['last_commit_date'][:10],  # Just the date part
                    branch['last_commit_message'][:50] + "..." if len(branch['last_commit_message']) > 50 else branch['last_commit_message']
                )
                
            console.print(branches_table)
        
        # Branch health
        merged_count = len(activity.get('merged_branches', []))
        unmerged_count = len(activity.get('unmerged_branches', []))
        
        health_info = f"""
[cyan]Merged Branches:[/] {merged_count}
[cyan]Unmerged Branches:[/] {unmerged_count}
[cyan]Total Branches:[/] {merged_count + unmerged_count}
"""
        console.print(Panel(health_info, title="[blue]Branch Health", border_style="blue"))
        
        # Show unmerged branches if any
        if activity.get('unmerged_branches'):
            unmerged_list = "\n".join([f"• {branch}" for branch in activity['unmerged_branches'][:5]])
            if len(activity['unmerged_branches']) > 5:
                unmerged_list += f"\n... and {len(activity['unmerged_branches']) - 5} more"
            console.print(Panel(f"[yellow]Unmerged Branches:[/]\n{unmerged_list}", 
                              title="[yellow]Attention Needed", border_style="yellow"))

    def display_contributor_stats(self, stats):
        """Display contributor statistics"""
        if 'error' in stats:
            console.print(Panel(f"[red]Error: {stats['error']}[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        # Contributor summary
        if 'summary' in stats:
            console.print(Panel(f"[cyan]Contributor Summary:[/]\n{stats['summary']}", 
                              title="[blue]Contributors", border_style="blue"))
        
        # Recent contributions
        if 'details' in stats and stats['details']:
            recent_table = Table(title="[bold blue]Recent Contributions[/]", 
                                show_header=True, header_style="bold magenta", box=box.ROUNDED)
            recent_table.add_column("Hash", style="cyan", no_wrap=True)
            recent_table.add_column("Author", style="white")
            recent_table.add_column("Date", style="green")
            recent_table.add_column("Message", style="yellow")
            
            for contrib in stats['details'][:10]:  # Show top 10
                recent_table.add_row(
                    contrib['hash'],
                    contrib['author'],
                    contrib['date'][:10],
                    contrib['message'][:40] + "..." if len(contrib['message']) > 40 else contrib['message']
                )
                
            console.print(recent_table)

    def display_repository_health(self, health):
        """Display repository health indicators"""
        if 'error' in health:
            console.print(Panel(f"[red]Error: {health['error']}[/]", 
                              title="[red]Error", border_style="red"))
            return
            
        # Health metrics
        health_table = Table(title="[bold blue]Repository Health[/]", 
                            show_header=True, header_style="bold magenta", box=box.ROUNDED)
        health_table.add_column("Metric", style="cyan", no_wrap=True)
        health_table.add_column("Value", style="white")
        
        health_table.add_row("Merge Commits", f"[bold green]{health.get('merge_commits', 0)}[/]")
        health_table.add_row("Orphaned Branches", f"[bold yellow]{health.get('orphaned_branches', 0)}[/]")
        
        console.print(health_table)
        
        # Size information
        if 'size_info' in health:
            console.print(Panel(f"[cyan]Repository Size:[/]\n{health['size_info']}", 
                              title="[blue]Size Information", border_style="blue"))
        
        # Large files warning
        if 'large_files' in health and health['large_files']:
            console.print(Panel(f"[yellow]Large Files Detected:[/]\n{health['large_files']}", 
                              title="[yellow]Performance Warning", border_style="yellow"))
        
        # Health score
        orphaned_branches = health.get('orphaned_branches', 0)
        if orphaned_branches == 0:
            health_score = "🟢 Excellent"
        elif orphaned_branches <= 3:
            health_score = "🟡 Good"
        else:
            health_score = "🔴 Needs Attention"
            
        console.print(Panel(f"[cyan]Overall Health:[/] {health_score}", 
                          title="[blue]Health Assessment", border_style="blue"))

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
    parser.add_argument('--github-login', action='store_true', help='Login to GitHub')
    parser.add_argument('--github-logout', action='store_true', help='Logout from GitHub')
    
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
    
    delete_branch_parser = branch_subparsers.add_parser('delete', help='Delete a local branch')
    delete_branch_parser.add_argument('name', help='Branch name to delete')
    delete_branch_parser.add_argument('--force', action='store_true', help='Force delete (even if not merged)')
    
    delete_remote_branch_parser = branch_subparsers.add_parser('delete-remote', help='Delete a remote branch')
    delete_remote_branch_parser.add_argument('name', help='Branch name to delete')
    delete_remote_branch_parser.add_argument('--remote', default='origin', help='Remote name (default: origin)')
    
    rename_branch_parser = branch_subparsers.add_parser('rename', help='Rename a branch')
    rename_branch_parser.add_argument('old_name', help='Current branch name')
    rename_branch_parser.add_argument('new_name', help='New branch name')
    
    checkout_parser = branch_subparsers.add_parser('checkout', help='Checkout a branch')
    checkout_parser.add_argument('ref', help='Branch or commit to checkout')
    
    merge_parser = branch_subparsers.add_parser('merge', help='Merge a branch')
    merge_parser.add_argument('branch', help='Branch to merge')
    
    rebase_parser = branch_subparsers.add_parser('rebase', help='Rebase current branch')
    rebase_parser.add_argument('branch', help='Branch to rebase onto')
    
    # Cherry-pick command
    cherry_pick_parser = subparsers.add_parser('cherry-pick', help='Cherry-pick a commit')
    cherry_pick_group = cherry_pick_parser.add_mutually_exclusive_group(required=True)
    cherry_pick_group.add_argument('commit', nargs='?', help='Commit hash to cherry-pick')
    cherry_pick_group.add_argument('--continue', action='store_true', help='Continue cherry-pick after resolving conflicts')
    cherry_pick_group.add_argument('--abort', action='store_true', help='Abort cherry-pick operation')
    cherry_pick_parser.add_argument('--no-commit', action='store_true', help='Do not automatically commit')
    
    # Revert command
    revert_parser = subparsers.add_parser('revert', help='Revert a commit')
    revert_group = revert_parser.add_mutually_exclusive_group(required=True)
    revert_group.add_argument('commit', nargs='?', help='Commit hash to revert')
    revert_group.add_argument('--continue', action='store_true', help='Continue revert after resolving conflicts')
    revert_group.add_argument('--abort', action='store_true', help='Abort revert operation')
    revert_parser.add_argument('--no-commit', action='store_true', help='Do not automatically commit')
    
    # Stash commands
    stash_parser = subparsers.add_parser('stash', help='Stash operations')
    stash_subparsers = stash_parser.add_subparsers(dest='stash_command')
    
    stash_list_parser = stash_subparsers.add_parser('list', help='List stashes')
    stash_list_parser.add_argument('--repo', required=True, help='Local repository path')

    stash_create_parser = stash_subparsers.add_parser('create', help='Create a new stash')
    stash_create_parser.add_argument('--repo', required=True, help='Local repository path')
    stash_create_parser.add_argument('--message', help='Stash message')

    stash_pop_parser = stash_subparsers.add_parser('pop', help='Pop a stash')
    stash_pop_parser.add_argument('--repo', required=True, help='Local repository path')
    stash_pop_parser.add_argument('--stash', help='Stash reference (e.g., stash@{0})')

    stash_drop_parser = stash_subparsers.add_parser('drop', help='Drop a stash')
    stash_drop_parser.add_argument('--repo', required=True, help='Local repository path')
    stash_drop_parser.add_argument('--stash', help='Stash reference (e.g., stash@{0})')
    
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
    
    # GitHub commands
    github_parser = subparsers.add_parser('github', help='GitHub operations')
    github_subparsers = github_parser.add_subparsers(dest='github_command')
    
    github_subparsers.add_parser('login', help='Login to GitHub')
    github_subparsers.add_parser('logout', help='Logout from GitHub')
    github_subparsers.add_parser('repos', help='List GitHub repositories')
    
    github_clone_parser = github_subparsers.add_parser('clone', help='Clone a GitHub repository')
    github_clone_parser.add_argument('name', help='Repository name')
    github_clone_parser.add_argument('--path', help='Target path for cloning')
    
    github_search_parser = github_subparsers.add_parser('search', help='Search GitHub repositories')
    github_search_parser.add_argument('query', help='Search query')
    github_search_parser.add_argument('--limit', type=int, default=20, help='Maximum number of results')
    
    # GitHub PRs commands
    github_prs_parser = github_subparsers.add_parser('prs', help='Manage GitHub pull requests')
    github_prs_subparsers = github_prs_parser.add_subparsers(dest='prs_command')
    
    github_prs_list_parser = github_prs_subparsers.add_parser('list', help='List pull requests for a repository')
    github_prs_list_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')
    github_prs_list_parser.add_argument('--state', choices=['open', 'closed', 'all'], default='open', help='PR state')
    github_prs_list_parser.add_argument('--label', help='Filter by label')
    github_prs_list_parser.add_argument('--assignee', help='Filter by assignee')
    github_prs_list_parser.add_argument('--limit', type=int, default=20, help='Maximum number of PRs to list')

    github_prs_create_parser = github_prs_subparsers.add_parser('create', help='Create a new pull request')
    github_prs_create_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')
    github_prs_create_parser.add_argument('--title', required=True, help='Title of the PR')
    github_prs_create_parser.add_argument('--head', required=True, help='Name of the branch where changes are implemented')
    github_prs_create_parser.add_argument('--base', required=True, help='Name of the branch you want the changes pulled into')
    github_prs_create_parser.add_argument('--body', help='Body/description of the PR')

    github_prs_comment_parser = github_prs_subparsers.add_parser('comment', help='Comment on a pull request')
    github_prs_comment_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')
    github_prs_comment_parser.add_argument('--pr', required=True, type=int, help='Pull request number')
    github_prs_comment_parser.add_argument('--body', required=True, help='Comment body')

    github_prs_close_parser = github_prs_subparsers.add_parser('close', help='Close a pull request')
    github_prs_close_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')
    github_prs_close_parser.add_argument('--pr', required=True, type=int, help='Pull request number')

    github_prs_merge_parser = github_prs_subparsers.add_parser('merge', help='Merge a pull request')
    github_prs_merge_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')
    github_prs_merge_parser.add_argument('--pr', required=True, type=int, help='Pull request number')
    github_prs_merge_parser.add_argument('--method', choices=['merge', 'squash', 'rebase'], default='merge', help='Merge method')

    github_prs_assign_parser = github_prs_subparsers.add_parser('assign', help='Assign a user to a pull request')
    github_prs_assign_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')
    github_prs_assign_parser.add_argument('--pr', required=True, type=int, help='Pull request number')
    github_prs_assign_parser.add_argument('--user', required=True, help='Username to assign')

    github_prs_label_parser = github_prs_subparsers.add_parser('label', help='Add a label to a pull request')
    github_prs_label_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')
    github_prs_label_parser.add_argument('--pr', required=True, type=int, help='Pull request number')
    github_prs_label_parser.add_argument('--label', required=True, help='Label to add')

    # GitHub notifications commands
    github_notifications_parser = github_subparsers.add_parser('notifications', help='Manage GitHub notifications')
    github_notifications_subparsers = github_notifications_parser.add_subparsers(dest='notifications_command')

    github_notifications_list_parser = github_notifications_subparsers.add_parser('list', help='List notifications')
    github_notifications_list_parser.add_argument('--all', action='store_true', help='List all notifications (not just unread)')

    github_notifications_mark_read_parser = github_notifications_subparsers.add_parser('mark-read', help='Mark notifications as read')
    github_notifications_mark_read_parser.add_argument('--id', help='Notification thread ID to mark as read')
    github_notifications_mark_read_parser.add_argument('--all', action='store_true', help='Mark all notifications as read')

    # GitHub releases commands
    github_releases_parser = github_subparsers.add_parser('releases', help='Manage GitHub releases')
    github_releases_subparsers = github_releases_parser.add_subparsers(dest='releases_command')

    github_releases_list_parser = github_releases_subparsers.add_parser('list', help='List releases for a repository')
    github_releases_list_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')
    github_releases_list_parser.add_argument('--limit', type=int, default=20, help='Maximum number of releases to list')

    github_releases_create_parser = github_releases_subparsers.add_parser('create', help='Create a new release')
    github_releases_create_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')
    github_releases_create_parser.add_argument('--tag', required=True, help='Tag name for the release')
    github_releases_create_parser.add_argument('--title', required=True, help='Release title')
    github_releases_create_parser.add_argument('--body', help='Release description/body')
    github_releases_create_parser.add_argument('--draft', action='store_true', help='Create as draft release')
    github_releases_create_parser.add_argument('--prerelease', action='store_true', help='Mark as prerelease')

    github_stats_parser = github_subparsers.add_parser('stats', help='Show repository stats')
    github_stats_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')

    # GitHub branches commands
    github_branches_parser = github_subparsers.add_parser('branches', help='Branch operations')
    github_branches_subparsers = github_branches_parser.add_subparsers(dest='branches_command')

    github_branches_graph_parser = github_branches_subparsers.add_parser('graph', help='Show branch graph')
    github_branches_graph_parser.add_argument('--repo', required=True, help='Repository in the form owner/repo')

    # Tag commands
    tag_parser = subparsers.add_parser('tag', help='Tag operations')
    tag_subparsers = tag_parser.add_subparsers(dest='tag_command')

    tag_list_parser = tag_subparsers.add_parser('list', help='List all tags')
    tag_list_parser.add_argument('--repo', required=True, help='Local repository path')

    tag_create_parser = tag_subparsers.add_parser('create', help='Create a new tag')
    tag_create_parser.add_argument('--repo', required=True, help='Local repository path')
    tag_create_parser.add_argument('name', help='Tag name')
    tag_create_parser.add_argument('--message', help='Tag message (for annotated tag)')
    tag_create_parser.add_argument('--annotated', action='store_true', help='Create an annotated tag')
    tag_create_parser.add_argument('--commit', help='Commit hash to tag (default: HEAD)')

    tag_delete_parser = tag_subparsers.add_parser('delete', help='Delete a tag')
    tag_delete_parser.add_argument('--repo', required=True, help='Local repository path')
    tag_delete_parser.add_argument('name', help='Tag name to delete')

    tag_show_parser = tag_subparsers.add_parser('show', help='Show tag details')
    tag_show_parser.add_argument('--repo', required=True, help='Local repository path')
    tag_show_parser.add_argument('name', help='Tag name to show')

    # Interactive rebase command
    rebase_interactive_parser = subparsers.add_parser('rebase-interactive', help='Interactive rebase onto a base branch or commit')
    rebase_interactive_parser.add_argument('base', help='Base branch or commit to rebase onto')

    # Squash command
    squash_parser = subparsers.add_parser('squash', help='Squash last N commits into one')
    squash_parser.add_argument('num', type=int, help='Number of commits to squash (from HEAD)')
    squash_parser.add_argument('--message', help='Commit message for the squashed commit')

    # Log for a specific file
    log_file_parser = subparsers.add_parser('log-file', help='Show commit log for a specific file')
    log_file_parser.add_argument('file', help='File path')
    log_file_parser.add_argument('--max-count', type=int, default=20, help='Maximum number of commits')

    # Show commit details
    show_commit_parser = subparsers.add_parser('show-commit', help='Show full details for a specific commit')
    show_commit_parser.add_argument('hash', help='Commit hash')

    # Repository Analytics commands
    analytics_parser = subparsers.add_parser('analytics', help='Repository analytics and statistics')
    analytics_subparsers = analytics_parser.add_subparsers(dest='analytics_command')

    analytics_stats_parser = analytics_subparsers.add_parser('stats', help='Show comprehensive repository statistics')

    analytics_activity_parser = analytics_subparsers.add_parser('activity', help='Show commit activity over time')
    analytics_activity_parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')

    analytics_files_parser = analytics_subparsers.add_parser('files', help='Show file change statistics')
    analytics_files_parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')

    analytics_branches_parser = analytics_subparsers.add_parser('branches', help='Show branch activity and health')

    analytics_contributors_parser = analytics_subparsers.add_parser('contributors', help='Show contributor statistics')

    analytics_health_parser = analytics_subparsers.add_parser('health', help='Show repository health indicators')

    args = parser.parse_args()
    
    # Handle special modes
    if args.interactive:
        async def run_interactive():
            await cli.initialize()
            await cli.interactive_mode()
        asyncio.run(run_interactive())
        return
        
    if args.discover:
        cli.show_repository_discovery()
        return
        
    if args.github_login:
        async def run_github_login():
            await cli.initialize()
            await cli.github_login()
        asyncio.run(run_github_login())
        return
        
    if args.github_logout:
        cli.github_logout()
        return
        
    if not args.command:
        parser.print_help()
        return

    # Only require --repo for commands that need a local repo
    commands_require_repo = [
        'status', 'log', 'branch', 'commit', 'push', 'pull', 'gitflow', 'cherry-pick', 'revert', 'analytics'
    ]
    if args.command in commands_require_repo and not args.repo:
        console.print(Panel("[bold red]❌ Repository path is required. Use --repo <path>[/]", 
                          title="[red]Error", border_style="red"))
        return
        
    async def run():
        await cli.initialize()

        # Only set repository for commands that require it
        if args.command in commands_require_repo:
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
            elif args.branch_command == 'delete':
                git_ops = GitOperations(args.repo)
                result = await git_ops.delete_branch(args.name, args.force)
                print(result)
            elif args.branch_command == 'delete-remote':
                git_ops = GitOperations(args.repo)
                result = await git_ops.delete_remote_branch(args.name, args.remote)
                print(result)
            elif args.branch_command == 'rename':
                git_ops = GitOperations(args.repo)
                result = await git_ops.rename_branch(args.old_name, args.new_name)
                print(result)
            elif args.branch_command == 'checkout':
                await cli.checkout(args.ref)
            elif args.branch_command == 'merge':
                await cli.merge(args.branch)
            elif args.branch_command == 'rebase':
                await cli.rebase(args.branch)
        elif args.command == 'stash':
            git_ops = GitOperations(args.repo)
            if args.stash_command == 'list':
                result = await git_ops.stash_list()
                print(result)
            elif args.stash_command == 'create':
                result = await git_ops.stash(args.message)
                print(result)
            elif args.stash_command == 'pop':
                result = await git_ops.stash_pop(args.stash or 'stash@{0}')
                print(result)
            elif args.stash_command == 'drop':
                result = await git_ops.drop_stash(args.stash or 'stash@{0}')
                print(result)
            else:
                parser.print_help()
                return
        elif args.command == 'tag':
            git_ops = GitOperations(args.repo)
            if args.tag_command == 'list':
                result = await git_ops.list_tags()
                print(result)
            elif args.tag_command == 'create':
                result = await git_ops.create_tag(args.name, message=args.message, annotated=args.annotated, commit=args.commit)
                print(result)
            elif args.tag_command == 'delete':
                result = await git_ops.delete_tag(args.name)
                print(result)
            elif args.tag_command == 'show':
                result = await git_ops.show_tag_details(args.name)
                print(result)
            else:
                parser.print_help()
                return
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
        elif args.command == 'cherry-pick':
            git_ops = GitOperations(args.repo)
            if args.abort:
                result = await git_ops._run_git_command('cherry-pick', '--abort')
                print(result)
            elif getattr(args, 'continue', False):
                result = await git_ops._run_git_command('cherry-pick', '--continue')
                print(result)
            elif args.commit:
                cmd = ['cherry-pick']
                if args.no_commit:
                    cmd.append('--no-commit')
                cmd.append(args.commit)
                result = await git_ops._run_git_command(*cmd)
                print(result)
        elif args.command == 'revert':
            git_ops = GitOperations(args.repo)
            if args.abort:
                result = await git_ops._run_git_command('revert', '--abort')
                print(result)
            elif getattr(args, 'continue', False):
                result = await git_ops._run_git_command('revert', '--continue')
                print(result)
            elif args.commit:
                cmd = ['revert']
                if args.no_commit:
                    cmd.append('--no-commit')
                cmd.append(args.commit)
                result = await git_ops._run_git_command(*cmd)
                print(result)
        elif args.command == 'github':
            if args.github_command == 'login':
                await cli.github_login()
            elif args.github_command == 'logout':
                cli.github_logout()
            elif args.github_command == 'repos':
                await cli.github_list_repos()
            elif args.github_command == 'clone':
                success = await cli.github_repos.clone_repository(args.name)
                if success and Confirm.ask("Set this as current repository?"):
                    if args.path:
                        cli.set_repository(args.path)
                    else:
                        user_info = cli.github_auth.get_user_info()
                        if user_info:
                            repo_path = Path.home() / "git" / user_info['login'] / args.name
                            if repo_path.exists():
                                cli.set_repository(str(repo_path))
            elif args.github_command == 'search':
                repos = await cli.github_repos.search_repositories(args.query, args.limit)
                cli.github_repos.display_repositories(repos)
            elif hasattr(args, 'prs_command') and args.prs_command:
                if args.prs_command == 'list':
                    kwargs = {}
                    if args.label is not None:
                        kwargs['label'] = args.label
                    if args.assignee is not None:
                        kwargs['assignee'] = args.assignee
                    await cli.github_repos.list_pull_requests(args.repo, args.state, args.limit, **kwargs)
                elif args.prs_command == 'create':
                    await cli.github_repos.create_pull_request(args.repo, args.title, args.head, args.base, args.body or "")
                elif args.prs_command == 'comment':
                    await cli.github_repos.comment_pull_request(args.repo, int(args.pr), args.body)
                elif args.prs_command == 'close':
                    await cli.github_repos.close_pull_request(args.repo, int(args.pr))
                elif args.prs_command == 'merge':
                    await cli.github_repos.merge_pull_request(args.repo, int(args.pr), args.method)
                elif args.prs_command == 'assign':
                    await cli.github_repos.assign_pull_request(args.repo, int(args.pr), args.user)
                elif args.prs_command == 'label':
                    await cli.github_repos.label_pull_request(args.repo, int(args.pr), args.label)
            elif hasattr(args, 'notifications_command') and args.notifications_command:
                if args.notifications_command == 'list':
                    await cli.github_notifications_list_mode(args)
                elif args.notifications_command == 'mark-read':
                    await cli.github_notifications_mark_read_mode(args)
            elif hasattr(args, 'releases_command') and args.releases_command:
                if args.releases_command == 'list':
                    await cli.github_releases_list_mode(args)
                elif args.releases_command == 'create':
                    await cli.github_releases_create_mode(args)
            elif getattr(args, 'github_command', None) == 'stats':
                await cli.github_stats_mode(args.repo)
            elif hasattr(args, 'branches_command') and args.branches_command:
                if args.branches_command == 'graph':
                    await cli.github_branches_graph_mode(args)
        elif args.command == 'rebase-interactive':
            await cli.rebase_interactive(args.base)
        elif args.command == 'squash':
            await cli.squash(args.num, args.message)
        elif args.command == 'log-file':
            git_ops = GitOperations(args.repo)
            result = await git_ops.file_log(args.file, args.max_count)
            print(result if result else '[No log output]')
        elif args.command == 'show-commit':
            git_ops = GitOperations(args.repo)
            result = await git_ops.show_commit(args.hash)
            print(result if result else '[No commit details output]')
        elif args.command == 'analytics':
            if not args.repo:
                console.print(Panel("[bold red]❌ Repository path is required. Use --repo <path>[/]", 
                                  title="[red]Error", border_style="red"))
                return
            git_ops = GitOperations(args.repo)
            if args.analytics_command == 'stats':
                result = await git_ops.get_repository_stats()
                cli.display_repository_stats(result)
            elif args.analytics_command == 'activity':
                result = await git_ops.get_commit_activity(args.days)
                cli.display_commit_activity(result, args.days)
            elif args.analytics_command == 'files':
                result = await git_ops.get_file_changes(args.days)
                cli.display_file_changes(result, args.days)
            elif args.analytics_command == 'branches':
                result = await git_ops.get_branch_activity()
                cli.display_branch_activity(result)
            elif args.analytics_command == 'contributors':
                result = await git_ops.get_contributor_stats()
                cli.display_contributor_stats(result)
            elif args.analytics_command == 'health':
                result = await git_ops.get_repository_health()
                cli.display_repository_health(result)
            else:
                parser.print_help()
                return
        else:
            parser.print_help()
            return
    
    asyncio.run(run())

if __name__ == "__main__":
    main() 