"""
Advanced search functionality for GitFlow Studio
Allows users to find code across multiple repositories with various search criteria
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.text import Text

console = Console()

class AdvancedSearch:
    """Advanced search functionality for GitFlow Studio"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
        self.search_results = []
    
    def search_code(self, query: str, repos: List[str] = None, file_types: List[str] = None,
                   case_sensitive: bool = False, regex: bool = False, 
                   exclude_patterns: List[str] = None) -> List[Dict[str, Any]]:
        """Search for code across repositories"""
        if not repos:
            repos = self._discover_repositories()
        
        if not file_types:
            file_types = ["*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c", "*.h", "*.go", "*.rs", "*.php"]
        
        if not exclude_patterns:
            exclude_patterns = ["node_modules", ".git", "__pycache__", "*.pyc", "*.log"]
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching code...", total=len(repos))
            
            for repo_path in repos:
                progress.update(task, description=f"Searching {Path(repo_path).name}...")
                
                repo_results = self._search_in_repository(
                    repo_path, query, file_types, case_sensitive, regex, exclude_patterns
                )
                results.extend(repo_results)
                
                progress.advance(task)
        
        self.search_results = results
        return results
    
    def search_commits(self, query: str, repos: List[str] = None, 
                      author: str = None, since: str = None, until: str = None) -> List[Dict[str, Any]]:
        """Search for commits containing specific text"""
        if not repos:
            repos = self._discover_repositories()
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching commits...", total=len(repos))
            
            for repo_path in repos:
                progress.update(task, description=f"Searching commits in {Path(repo_path).name}...")
                
                repo_results = self._search_commits_in_repository(
                    repo_path, query, author, since, until
                )
                results.extend(repo_results)
                
                progress.advance(task)
        
        return results
    
    def search_files(self, filename_pattern: str, repos: List[str] = None,
                    file_types: List[str] = None, size_min: int = None, size_max: int = None) -> List[Dict[str, Any]]:
        """Search for files by name pattern"""
        if not repos:
            repos = self._discover_repositories()
        
        if not file_types:
            file_types = ["*"]
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching files...", total=len(repos))
            
            for repo_path in repos:
                progress.update(task, description=f"Searching files in {Path(repo_path).name}...")
                
                repo_results = self._search_files_in_repository(
                    repo_path, filename_pattern, file_types, size_min, size_max
                )
                results.extend(repo_results)
                
                progress.advance(task)
        
        return results
    
    def search_history(self, file_path: str, query: str = None, author: str = None,
                      since: str = None, until: str = None) -> List[Dict[str, Any]]:
        """Search file history for changes"""
        if not Path(file_path).exists():
            console.print(f"[red]File not found: {file_path}[/]")
            return []
        
        try:
            cmd = ["git", "log", "--follow", "--oneline", "--format=%H|%an|%ad|%s", "--date=short"]
            
            if author:
                cmd.extend(["--author", author])
            if since:
                cmd.extend(["--since", since])
            if until:
                cmd.extend(["--until", until])
            
            cmd.append(file_path)
            
            result = subprocess.run(cmd, cwd=Path(file_path).parent, 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return []
            
            history = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commit_hash, author_name, date, message = parts[:4]
                        
                        # Filter by query if provided
                        if query and query.lower() not in message.lower():
                            continue
                        
                        history.append({
                            "commit_hash": commit_hash,
                            "author": author_name,
                            "date": date,
                            "message": message,
                            "file": file_path
                        })
            
            return history
        except Exception as e:
            console.print(f"[red]Error searching file history: {e}[/]")
            return []
    
    def search_dependencies(self, package_name: str, repos: List[str] = None) -> List[Dict[str, Any]]:
        """Search for dependencies across repositories"""
        if not repos:
            repos = self._discover_repositories()
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching dependencies...", total=len(repos))
            
            for repo_path in repos:
                progress.update(task, description=f"Searching dependencies in {Path(repo_path).name}...")
                
                repo_results = self._search_dependencies_in_repository(repo_path, package_name)
                if repo_results:
                    results.extend(repo_results)
                
                progress.advance(task)
        
        return results
    
    def _discover_repositories(self) -> List[str]:
        """Discover Git repositories in the base path"""
        repos = []
        
        for root, dirs, files in os.walk(self.base_path):
            if '.git' in dirs:
                repos.append(root)
                # Don't search inside .git directories
                dirs[:] = [d for d in dirs if d != '.git']
        
        return repos
    
    def _search_in_repository(self, repo_path: str, query: str, file_types: List[str],
                            case_sensitive: bool, regex: bool, exclude_patterns: List[str]) -> List[Dict[str, Any]]:
        """Search for code in a specific repository"""
        results = []
        
        try:
            # Build grep command
            cmd = ["grep", "-r", "-n"]
            
            if not case_sensitive:
                cmd.append("-i")
            
            if regex:
                cmd.append("-E")
            
            # Add exclude patterns
            for pattern in exclude_patterns:
                cmd.extend(["--exclude", pattern])
            
            # Add file type patterns
            for file_type in file_types:
                cmd.extend(["--include", file_type])
            
            cmd.extend([query, repo_path])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        match = self._parse_grep_line(line, repo_path)
                        if match:
                            results.append(match)
            
        except subprocess.TimeoutExpired:
            console.print(f"[yellow]Search timeout for {repo_path}[/]")
        except Exception as e:
            console.print(f"[red]Error searching in {repo_path}: {e}[/]")
        
        return results
    
    def _search_commits_in_repository(self, repo_path: str, query: str, author: str,
                                    since: str, until: str) -> List[Dict[str, Any]]:
        """Search for commits in a specific repository"""
        results = []
        
        try:
            cmd = ["git", "log", "--oneline", "--format=%H|%an|%ad|%s", "--date=short", "--grep", query]
            
            if author:
                cmd.extend(["--author", author])
            if since:
                cmd.extend(["--since", since])
            if until:
                cmd.extend(["--until", until])
            
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 4:
                            commit_hash, author_name, date, message = parts[:4]
                            results.append({
                                "commit_hash": commit_hash,
                                "author": author_name,
                                "date": date,
                                "message": message,
                                "repository": repo_path
                            })
            
        except Exception as e:
            console.print(f"[red]Error searching commits in {repo_path}: {e}[/]")
        
        return results
    
    def _search_files_in_repository(self, repo_path: str, filename_pattern: str,
                                  file_types: List[str], size_min: int, size_max: int) -> List[Dict[str, Any]]:
        """Search for files in a specific repository"""
        results = []
        
        try:
            for file_type in file_types:
                pattern = filename_pattern.replace("*", ".*")
                regex = re.compile(pattern, re.IGNORECASE)
                
                for root, dirs, files in os.walk(repo_path):
                    # Skip .git directory
                    if '.git' in dirs:
                        dirs.remove('.git')
                    
                    for file in files:
                        if regex.search(file):
                            file_path = Path(root) / file
                            
                            # Check file size constraints
                            if size_min and file_path.stat().st_size < size_min:
                                continue
                            if size_max and file_path.stat().st_size > size_max:
                                continue
                            
                            results.append({
                                "file": str(file_path),
                                "name": file,
                                "size": file_path.stat().st_size,
                                "repository": repo_path,
                                "relative_path": str(file_path.relative_to(repo_path))
                            })
            
        except Exception as e:
            console.print(f"[red]Error searching files in {repo_path}: {e}[/]")
        
        return results
    
    def _search_dependencies_in_repository(self, repo_path: str, package_name: str) -> List[Dict[str, Any]]:
        """Search for dependencies in a specific repository"""
        results = []
        
        try:
            # Check common dependency files
            dependency_files = [
                "requirements.txt", "package.json", "pom.xml", "build.gradle",
                "Cargo.toml", "go.mod", "composer.json", "Gemfile"
            ]
            
            for dep_file in dependency_files:
                file_path = Path(repo_path) / dep_file
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if package_name.lower() in content.lower():
                            results.append({
                                "repository": repo_path,
                                "file": str(file_path),
                                "package": package_name,
                                "content_preview": content[:200] + "..." if len(content) > 200 else content
                            })
            
        except Exception as e:
            console.print(f"[red]Error searching dependencies in {repo_path}: {e}[/]")
        
        return results
    
    def _parse_grep_line(self, line: str, repo_path: str) -> Optional[Dict[str, Any]]:
        """Parse a line from grep output"""
        try:
            # Format: file:line:content
            parts = line.split(':', 2)
            if len(parts) >= 3:
                file_path, line_num, content = parts
                
                return {
                    "file": file_path,
                    "line": int(line_num),
                    "content": content.strip(),
                    "repository": repo_path,
                    "relative_path": str(Path(file_path).relative_to(repo_path))
                }
        except Exception:
            pass
        
        return None
    
    def display_search_results(self, results: List[Dict[str, Any]], show_content: bool = True):
        """Display search results in a formatted table"""
        if not results:
            console.print(Panel("[yellow]No search results found.[/]", 
                              title="[blue]Search Results", border_style="blue"))
            return
        
        table = Table(
            title=f"[bold blue]Search Results[/]\n[dim]Found {len(results)} matches[/]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="blue"
        )
        
        table.add_column("Repository", style="cyan", no_wrap=True)
        table.add_column("File", style="white")
        table.add_column("Line", style="green", justify="right")
        
        if show_content:
            table.add_column("Content", style="yellow")
        
        for result in results[:100]:  # Limit to first 100 results
            repo_name = Path(result.get("repository", "")).name
            file_name = result.get("relative_path", result.get("file", ""))
            line_num = str(result.get("line", ""))
            
            row = [repo_name, file_name, line_num]
            
            if show_content:
                content = result.get("content", "")
                # Truncate long content
                if len(content) > 80:
                    content = content[:77] + "..."
                row.append(content)
            
            table.add_row(*row)
        
        console.print(table)
        
        if len(results) > 100:
            console.print(f"[yellow]Showing first 100 results. Total: {len(results)}[/]")
    
    def display_commit_results(self, results: List[Dict[str, Any]]):
        """Display commit search results"""
        if not results:
            console.print(Panel("[yellow]No commit matches found.[/]", 
                              title="[blue]Commit Search Results", border_style="blue"))
            return
        
        table = Table(
            title=f"[bold blue]Commit Search Results[/]\n[dim]Found {len(results)} commits[/]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="blue"
        )
        
        table.add_column("Repository", style="cyan", no_wrap=True)
        table.add_column("Commit", style="green", no_wrap=True)
        table.add_column("Author", style="white")
        table.add_column("Date", style="yellow")
        table.add_column("Message", style="blue")
        
        for result in results[:50]:  # Limit to first 50 results
            repo_name = Path(result.get("repository", "")).name
            commit_hash = result.get("commit_hash", "")[:8]
            author = result.get("author", "")
            date = result.get("date", "")
            message = result.get("message", "")
            
            # Truncate long message
            if len(message) > 60:
                message = message[:57] + "..."
            
            table.add_row(repo_name, commit_hash, author, date, message)
        
        console.print(table)
        
        if len(results) > 50:
            console.print(f"[yellow]Showing first 50 results. Total: {len(results)}[/]")
    
    def display_file_results(self, results: List[Dict[str, Any]]):
        """Display file search results"""
        if not results:
            console.print(Panel("[yellow]No file matches found.[/]", 
                              title="[blue]File Search Results", border_style="blue"))
            return
        
        table = Table(
            title=f"[bold blue]File Search Results[/]\n[dim]Found {len(results)} files[/]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="blue"
        )
        
        table.add_column("Repository", style="cyan", no_wrap=True)
        table.add_column("File", style="white")
        table.add_column("Size", style="green", justify="right")
        
        for result in results[:100]:  # Limit to first 100 results
            repo_name = Path(result.get("repository", "")).name
            file_name = result.get("relative_path", result.get("file", ""))
            size = self._format_file_size(result.get("size", 0))
            
            table.add_row(repo_name, file_name, size)
        
        console.print(table)
        
        if len(results) > 100:
            console.print(f"[yellow]Showing first 100 results. Total: {len(results)}[/]")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def export_search_results(self, results: List[Dict[str, Any]], format: str = "json",
                            filename: Optional[str] = None) -> str:
        """Export search results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_results_{timestamp}.{format}"
        
        file_path = Path.cwd() / filename
        
        try:
            if format.lower() == "json":
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            elif format.lower() == "csv":
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if results:
                        writer = csv.writer(f)
                        # Get all possible keys
                        all_keys = set()
                        for result in results:
                            all_keys.update(result.keys())
                        
                        headers = sorted(all_keys)
                        writer.writerow(headers)
                        
                        for result in results:
                            row = [result.get(key, "") for key in headers]
                            writer.writerow(row)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            console.print(f"[green]✅ Search results exported to {file_path}[/]")
            return str(file_path)
        except Exception as e:
            console.print(f"[red]Error exporting search results: {e}[/]")
            return "" 