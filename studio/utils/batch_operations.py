"""
Batch Operations Manager for GitFlow Studio
Provides functionality to perform operations across multiple repositories simultaneously
"""

import os
import asyncio
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.live import Live
from rich.layout import Layout

console = Console()

class BatchOperationsManager:
    """Manages batch operations across multiple repositories"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.results = []
        self.failed_operations = []
    
    async def batch_status(self, repo_paths: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get status for multiple repositories"""
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Checking repository status...", total=len(repo_paths))
            
            async def check_repo_status(repo_path: str):
                try:
                    # Simulate Git status check
                    import subprocess
                    result = subprocess.run(
                        ["git", "status", "--porcelain"], 
                        cwd=repo_path, 
                        capture_output=True, 
                        text=True, 
                        timeout=10
                    )
                    
                    return {
                        "path": repo_path,
                        "status": "clean" if not result.stdout.strip() else "dirty",
                        "output": result.stdout.strip(),
                        "success": True
                    }
                except Exception as e:
                    return {
                        "path": repo_path,
                        "status": "error",
                        "error": str(e),
                        "success": False
                    }
            
            # Execute operations concurrently
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def limited_check(repo_path):
                async with semaphore:
                    return await check_repo_status(repo_path)
            
            tasks = [limited_check(repo_path) for repo_path in repo_paths]
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results_list):
                if isinstance(result, Exception):
                    results[repo_paths[i]] = {
                        "path": repo_paths[i],
                        "status": "error",
                        "error": str(result),
                        "success": False
                    }
                else:
                    results[repo_paths[i]] = result
                progress.advance(task)
        
        return results
    
    async def batch_pull(self, repo_paths: List[str], remote: str = "origin") -> Dict[str, Dict[str, Any]]:
        """Pull latest changes from multiple repositories"""
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Pulling from repositories...", total=len(repo_paths))
            
            async def pull_repo(repo_path: str):
                try:
                    import subprocess
                    
                    # Check current branch
                    branch_result = subprocess.run(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
                    
                    # Pull changes
                    pull_result = subprocess.run(
                        ["git", "pull", remote, current_branch],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    return {
                        "path": repo_path,
                        "branch": current_branch,
                        "success": pull_result.returncode == 0,
                        "output": pull_result.stdout.strip(),
                        "error": pull_result.stderr.strip() if pull_result.returncode != 0 else None
                    }
                except Exception as e:
                    return {
                        "path": repo_path,
                        "success": False,
                        "error": str(e)
                    }
            
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def limited_pull(repo_path):
                async with semaphore:
                    return await pull_repo(repo_path)
            
            tasks = [limited_pull(repo_path) for repo_path in repo_paths]
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results_list):
                if isinstance(result, Exception):
                    results[repo_paths[i]] = {
                        "path": repo_paths[i],
                        "success": False,
                        "error": str(result)
                    }
                else:
                    results[repo_paths[i]] = result
                progress.advance(task)
        
        return results
    
    async def batch_push(self, repo_paths: List[str], remote: str = "origin") -> Dict[str, Dict[str, Any]]:
        """Push changes to multiple repositories"""
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Pushing to repositories...", total=len(repo_paths))
            
            async def push_repo(repo_path: str):
                try:
                    import subprocess
                    
                    # Check current branch
                    branch_result = subprocess.run(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
                    
                    # Push changes
                    push_result = subprocess.run(
                        ["git", "push", remote, current_branch],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    return {
                        "path": repo_path,
                        "branch": current_branch,
                        "success": push_result.returncode == 0,
                        "output": push_result.stdout.strip(),
                        "error": push_result.stderr.strip() if push_result.returncode != 0 else None
                    }
                except Exception as e:
                    return {
                        "path": repo_path,
                        "success": False,
                        "error": str(e)
                    }
            
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def limited_push(repo_path):
                async with semaphore:
                    return await push_repo(repo_path)
            
            tasks = [limited_push(repo_path) for repo_path in repo_paths]
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results_list):
                if isinstance(result, Exception):
                    results[repo_paths[i]] = {
                        "path": repo_paths[i],
                        "success": False,
                        "error": str(result)
                    }
                else:
                    results[repo_paths[i]] = result
                progress.advance(task)
        
        return results
    
    async def batch_branch_create(self, repo_paths: List[str], branch_name: str, 
                                 from_branch: str = None) -> Dict[str, Dict[str, Any]]:
        """Create a branch in multiple repositories"""
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Creating branch '{branch_name}'...", total=len(repo_paths))
            
            async def create_branch(repo_path: str):
                try:
                    import subprocess
                    
                    # Create branch
                    if from_branch:
                        cmd = ["git", "checkout", "-b", branch_name, from_branch]
                    else:
                        cmd = ["git", "checkout", "-b", branch_name]
                    
                    result = subprocess.run(
                        cmd,
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    return {
                        "path": repo_path,
                        "branch": branch_name,
                        "success": result.returncode == 0,
                        "output": result.stdout.strip(),
                        "error": result.stderr.strip() if result.returncode != 0 else None
                    }
                except Exception as e:
                    return {
                        "path": repo_path,
                        "success": False,
                        "error": str(e)
                    }
            
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def limited_create(repo_path):
                async with semaphore:
                    return await create_branch(repo_path)
            
            tasks = [limited_create(repo_path) for repo_path in repo_paths]
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results_list):
                if isinstance(result, Exception):
                    results[repo_paths[i]] = {
                        "path": repo_paths[i],
                        "success": False,
                        "error": str(result)
                    }
                else:
                    results[repo_paths[i]] = result
                progress.advance(task)
        
        return results
    
    async def batch_analytics(self, repo_paths: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get analytics for multiple repositories"""
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing repositories...", total=len(repo_paths))
            
            async def analyze_repo(repo_path: str):
                try:
                    import subprocess
                    
                    # Get basic repository information
                    stats = {}
                    
                    # Commit count
                    commit_result = subprocess.run(
                        ["git", "rev-list", "--count", "HEAD"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    stats["commit_count"] = int(commit_result.stdout.strip()) if commit_result.returncode == 0 else 0
                    
                    # Branch count
                    branch_result = subprocess.run(
                        ["git", "branch", "-r"] if True else ["git", "branch"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    stats["branch_count"] = len([b for b in branch_result.stdout.split('\n') if b.strip()]) if branch_result.returncode == 0 else 0
                    
                    # Last commit date
                    last_commit_result = subprocess.run(
                        ["git", "log", "-1", "--pretty=format:%ct"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if last_commit_result.returncode == 0:
                        timestamp = int(last_commit_result.stdout.strip())
                        stats["last_commit"] = datetime.fromtimestamp(timestamp).isoformat()
                    
                    # Repository size (approximate)
                    size_result = subprocess.run(
                        ["du", "-sh", ".git"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    stats["repo_size"] = size_result.stdout.split()[0] if size_result.returncode == 0 else "unknown"
                    
                    return {
                        "path": repo_path,
                        "success": True,
                        "analytics": stats
                    }
                except Exception as e:
                    return {
                        "path": repo_path,
                        "success": False,
                        "error": str(e)
                    }
            
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def limited_analyze(repo_path):
                async with semaphore:
                    return await analyze_repo(repo_path)
            
            tasks = [limited_analyze(repo_path) for repo_path in repo_paths]
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results_list):
                if isinstance(result, Exception):
                    results[repo_paths[i]] = {
                        "path": repo_paths[i],
                        "success": False,
                        "error": str(result)
                    }
                else:
                    results[repo_paths[i]] = result
                progress.advance(task)
        
        return results
    
    def display_batch_results(self, results: Dict[str, Dict[str, Any]], operation: str):
        """Display batch operation results in a formatted table"""
        if not results:
            console.print("[yellow]No results to display[/]")
            return
        
        table = Table(title=f"Batch {operation.title()} Results", box=box.ROUNDED)
        table.add_column("Repository", style="cyan", max_width=40)
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")
        
        success_count = 0
        total_count = len(results)
        
        for repo_path, result in results.items():
            repo_name = Path(repo_path).name
            
            if result.get("success", False):
                status = "✅ Success"
                details = result.get("output", "") or result.get("branch", "") or "Completed"
                success_count += 1
            else:
                status = "❌ Failed"
                details = result.get("error", "Unknown error")
            
            # Truncate long details
            if len(details) > 60:
                details = details[:57] + "..."
            
            table.add_row(repo_name, status, details)
        
        console.print(table)
        
        # Summary
        summary_text = f"[bold]Summary:[/] {success_count}/{total_count} repositories {operation}ed successfully"
        if success_count == total_count:
            console.print(Panel(summary_text, border_style="green"))
        elif success_count > 0:
            console.print(Panel(summary_text, border_style="yellow"))
        else:
            console.print(Panel(summary_text, border_style="red"))
    
    def discover_repositories(self, base_path: str = ".", max_depth: int = 3) -> List[str]:
        """Discover Git repositories in a directory tree"""
        repos = []
        base_path = Path(base_path).resolve()
        
        def find_repos(directory: Path, current_depth: int):
            if current_depth > max_depth:
                return
            
            try:
                # Check if current directory is a Git repository
                if (directory / ".git").exists():
                    repos.append(str(directory))
                    return  # Don't search inside Git repositories
                
                # Search subdirectories
                for item in directory.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        find_repos(item, current_depth + 1)
                        
            except PermissionError:
                pass  # Skip directories we can't access
        
        find_repos(base_path, 0)
        return repos
