"""
Backup and Restore Manager for GitFlow Studio
Provides comprehensive backup and restore functionality for repositories and data
"""

import os
import json
import shutil
import gzip
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm

console = Console()

class BackupRestoreManager:
    """Manages backup and restore operations for repositories and GitFlow Studio data"""
    
    def __init__(self, backup_dir: Optional[str] = None, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.gitflow-studio")
        self.backup_dir = Path(backup_dir) if backup_dir else Path(self.config_dir) / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_backup_structure()
    
    def _ensure_backup_structure(self):
        """Ensure backup directory structure exists"""
        directories = ["repositories", "config", "hooks", "aliases", "themes", "analytics"]
        for directory in directories:
            (self.backup_dir / directory).mkdir(parents=True, exist_ok=True)
    
    def create_repository_backup(self, repo_path: str, backup_name: str = None, 
                               include_history: bool = True, compression: str = "gzip") -> str:
        """Create a backup of a Git repository"""
        repo_path = Path(repo_path).resolve()
        
        if not (repo_path / ".git").exists():
            console.print(f"[red]Not a Git repository: {repo_path}[/]")
            return ""
        
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{repo_path.name}_{timestamp}"
        
        backup_path = self.backup_dir / "repositories" / f"{backup_name}.tar.gz"
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(f"Backing up {repo_path.name}...", total=100)
                
                # Create a bundle if include_history is True
                if include_history:
                    bundle_path = repo_path / f"{repo_path.name}.bundle"
                    progress.update(task, description="Creating Git bundle...")
                    
                    bundle_result = subprocess.run(
                        ["git", "bundle", "create", str(bundle_path), "--all"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if bundle_result.returncode != 0:
                        console.print(f"[red]Failed to create bundle: {bundle_result.stderr}[/]")
                        return ""
                    
                    progress.update(task, completed=30)
                
                # Create archive
                progress.update(task, description="Creating archive...", completed=40)
                
                with tarfile.open(backup_path, "w:gz") as tar:
                    # Add repository files
                    tar.add(repo_path, arcname=repo_path.name, 
                           filter=lambda tarinfo: None if '.git/objects' in tarinfo.name and tarinfo.size > 100000000 else tarinfo)
                    
                    progress.update(task, completed=80)
                
                # Clean up bundle file if created
                if include_history and bundle_path.exists():
                    bundle_path.unlink()
                
                progress.update(task, completed=100, description="Backup completed!")
            
            # Create backup metadata
            metadata = {
                "backup_name": backup_name,
                "repo_path": str(repo_path),
                "created": datetime.now().isoformat(),
                "include_history": include_history,
                "compression": compression,
                "size": backup_path.stat().st_size,
                "type": "repository"
            }
            
            metadata_path = self.backup_dir / "repositories" / f"{backup_name}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            console.print(f"[green]✅ Repository backup created: {backup_path}[/]")
            return str(backup_path)
            
        except Exception as e:
            console.print(f"[red]Error creating repository backup: {e}[/]")
            return ""
    
    def restore_repository(self, backup_name: str, restore_path: str = None, 
                         new_name: str = None) -> str:
        """Restore a repository from backup"""
        backup_file = self.backup_dir / "repositories" / f"{backup_name}.tar.gz"
        metadata_file = self.backup_dir / "repositories" / f"{backup_name}.json"
        
        if not backup_file.exists():
            console.print(f"[red]Backup file not found: {backup_file}[/]")
            return ""
        
        # Load metadata
        metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        
        # Determine restore path
        if not restore_path:
            # Try to restore to original location or ask user
            original_path = metadata.get("repo_path")
            if original_path and not Path(original_path).exists():
                restore_path = original_path
            else:
                restore_path = str(Path.cwd() / (new_name or backup_name))
        else:
            restore_path = Path(restore_path).resolve()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Restoring repository...", total=100)
                
                # Extract archive
                progress.update(task, description="Extracting archive...", completed=20)
                
                with tarfile.open(backup_file, "r:gz") as tar:
                    tar.extractall(Path(restore_path).parent)
                
                progress.update(task, completed=80)
                
                # Verify Git repository
                restored_repo = Path(restore_path)
                if (restored_repo / ".git").exists():
                    progress.update(task, description="Verifying repository...", completed=90)
                    
                    # Test Git commands
                    verify_result = subprocess.run(
                        ["git", "status"],
                        cwd=restored_repo,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if verify_result.returncode == 0:
                        progress.update(task, completed=100, description="Restore completed!")
                        console.print(f"[green]✅ Repository restored to: {restore_path}[/]")
                        return str(restore_path)
                    else:
                        console.print(f"[yellow]Warning: Repository restored but Git verification failed[/]")
                        return str(restore_path)
                else:
                    console.print(f"[red]Error: Restored directory is not a Git repository[/]")
                    return ""
        
        except Exception as e:
            console.print(f"[red]Error restoring repository: {e}[/]")
            return ""
    
    def backup_gitflow_config(self, backup_name: str = None) -> str:
        """Backup GitFlow Studio configuration"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"config_{timestamp}"
        
        config_backup_dir = self.backup_dir / "config" / backup_name
        config_backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            config_items = {
                "aliases": Path(self.config_dir) / "aliases.json",
                "themes": Path(self.config_dir) / "themes.json",
                "performance_metrics": Path(self.config_dir) / "performance_metrics.json",
                "hooks": Path(self.config_dir) / "hooks",
                "hook_templates": Path(self.config_dir) / "hook_templates"
            }
            
            backed_up_items = []
            
            for item_name, item_path in config_items.items():
                if item_path.exists():
                    if item_path.is_file():
                        shutil.copy2(item_path, config_backup_dir / f"{item_name}.json")
                    else:
                        shutil.copytree(item_path, config_backup_dir / item_name.name, dirs_exist_ok=True)
                    backed_up_items.append(item_name)
            
            # Create config metadata
            metadata = {
                "backup_name": backup_name,
                "created": datetime.now().isoformat(),
                "backed_up_items": backed_up_items,
                "config_dir": self.config_dir,
                "type": "configuration"
            }
            
            metadata_path = config_backup_dir / "config_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            console.print(f"[green]✅ Configuration backed up: {config_backup_dir}[/]")
            return str(config_backup_dir)
            
        except Exception as e:
            console.print(f"[red]Error backing up configuration: {e}[/]")
            return ""
    
    def restore_gitflow_config(self, backup_name: str) -> bool:
        """Restore GitFlow Studio configuration"""
        config_backup_dir = self.backup_dir / "config" / backup_name
        
        if not config_backup_dir.exists():
            console.print(f"[red]Configuration backup not found: {backup_name}[/]")
            return False
        
        metadata_file = config_backup_dir / "config_metadata.json"
        if not metadata_file.exists():
            console.print(f"[red]Configuration metadata not found[/]")
            return False
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            backed_up_items = metadata.get("backed_up_items", [])
            
            if not Confirm.ask("This will overwrite current configuration. Continue?"):
                console.print("[yellow]Configuration restore cancelled[/]")
                return False
            
            # Restore configuration files
            for item in config_backup_dir.iterdir():
                if item.name == "config_metadata.json":
                    continue
                
                target_path = Path(self.config_dir) / item.name
                
                if item.is_file() and item.suffix == ".json":
                    # Remove the .json suffix for the original filename
                    original_name = item.stem
                    if original_name == "aliases":
                        target_path = Path(self.config_dir) / "aliases.json"
                    elif original_name == "themes":
                        target_path = Path(self.config_dir) / "themes.json"
                    elif original_name == "performance_metrics":
                        target_path = Path(self.config_dir) / "performance_metrics.json"
                
                if item.is_file():
                    shutil.copy2(item, target_path)
                else:
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(item, target_path)
            
            console.print(f"[green]✅ Configuration restored from: {backup_name}[/]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error restoring configuration: {e}[/]")
            return False
    
    def create_full_backup(self, repo_paths: List[str] = None, backup_name: str = None) -> str:
        """Create a full backup of repositories and configuration"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"full_backup_{timestamp}"
        
        full_backup_dir = self.backup_dir / "full_backups" / backup_name
        full_backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            backed_up_repos = []
            backed_up_config = False
            
            # Backup repositories
            if repo_paths:
                for repo_path in repo_paths:
                    repo_backup = self.create_repository_backup(repo_path, 
                                                              f"{backup_name}_{Path(repo_path).name}")
                    if repo_backup:
                        shutil.move(repo_backup, full_backup_dir)
                        backed_up_repos.append(repo_path)
            else:
                # Auto-discover repositories
                discovered_repos = self._discover_repositories()
                for repo_path in discovered_repos:
                    repo_backup = self.create_repository_backup(repo_path, 
                                                              f"{backup_name}_{Path(repo_path).name}")
                    if repo_backup:
                        shutil.move(repo_backup, full_backup_dir)
                        backed_up_repos.append(repo_path)
            
            # Backup configuration
            config_backup = self.backup_gitflow_config(f"{backup_name}_config")
            if config_backup:
                shutil.move(config_backup, full_backup_dir)
                backed_up_config = True
            
            # Create full backup metadata
            metadata = {
                "backup_name": backup_name,
                "created": datetime.now().isoformat(),
                "type": "full_backup",
                "backed_up_repositories": backed_up_repos,
                "backed_up_config": backed_up_config,
                "backup_dir": str(full_backup_dir)
            }
            
            metadata_path = full_backup_dir / "full_backup_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            console.print(f"[green]✅ Full backup created: {full_backup_dir}[/]")
            return str(full_backup_dir)
            
        except Exception as e:
            console.print(f"[red]Error creating full backup: {e}[/]")
            return ""
    
    def list_backups(self, backup_type: str = "all") -> Dict[str, List[Dict[str, Any]]]:
        """List available backups"""
        backups = {
            "repositories": [],
            "config": [],
            "full_backups": []
        }
        
        # List repository backups
        repo_backup_dir = self.backup_dir / "repositories"
        if repo_backup_dir.exists():
            for backup_file in repo_backup_dir.glob("*.tar.gz"):
                metadata_file = repo_backup_dir / f"{backup_file.stem}.json"
                metadata = {}
                
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                
                backups["repositories"].append({
                    "name": backup_file.stem,
                    "file": str(backup_file),
                    "size": backup_file.stat().st_size,
                    "created": metadata.get("created", "unknown"),
                    "repo_path": metadata.get("repo_path", "unknown")
                })
        
        # List configuration backups
        config_backup_dir = self.backup_dir / "config"
        if config_backup_dir.exists():
            for backup_dir in config_backup_dir.iterdir():
                if backup_dir.is_dir():
                    metadata_file = backup_dir / "config_metadata.json"
                    metadata = {}
                    
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                    
                    backups["config"].append({
                        "name": backup_dir.name,
                        "path": str(backup_dir),
                        "created": metadata.get("created", "unknown"),
                        "items": metadata.get("backed_up_items", [])
                    })
        
        # List full backups
        full_backup_dir = self.backup_dir / "full_backups"
        if full_backup_dir.exists():
            for backup_dir in full_backup_dir.iterdir():
                if backup_dir.is_dir():
                    metadata_file = backup_dir / "full_backup_metadata.json"
                    metadata = {}
                    
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                    
                    backups["full_backups"].append({
                        "name": backup_dir.name,
                        "path": str(backup_dir),
                        "created": metadata.get("created", "unknown"),
                        "repos_count": len(metadata.get("backed_up_repositories", [])),
                        "config_backed": metadata.get("backed_up_config", False)
                    })
        
        return backups
    
    def display_backup_list(self, backup_type: str = "all"):
        """Display available backups in a formatted table"""
        backups = self.list_backups(backup_type)
        
        for backup_category, backup_list in backups.items():
            if not backup_list or (backup_type != "all" and backup_category != backup_type):
                continue
            
            table = Table(title=f"{backup_category.title()} Backups", box=box.ROUNDED)
            
            if backup_category == "repositories":
                table.add_column("Name", style="cyan")
                table.add_column("Repository", style="green")
                table.add_column("Size", justify="right", style="blue")
                table.add_column("Created", style="dim")
                
                for backup in backup_list:
                    size_mb = backup["size"] // (1024 * 1024)
                    repo_name = Path(backup["repo_path"]).name if backup["repo_path"] != "unknown" else "unknown"
                    table.add_row(
                        backup["name"],
                        repo_name,
                        f"{size_mb} MB",
                        backup["created"][:19] if backup["created"] != "unknown" else "unknown"
                    )
            
            elif backup_category == "config":
                table.add_column("Name", style="cyan")
                table.add_column("Items", style="green")
                table.add_column("Created", style="dim")
                
                for backup in backup_list:
                    items_str = ", ".join(backup["items"]) if backup["items"] else "none"
                    table.add_row(
                        backup["name"],
                        items_str,
                        backup["created"][:19] if backup["created"] != "unknown" else "unknown"
                    )
            
            elif backup_category == "full_backups":
                table.add_column("Name", style="cyan")
                table.add_column("Repositories", justify="right", style="green")
                table.add_column("Config", style="blue")
                table.add_column("Created", style="dim")
                
                for backup in backup_list:
                    config_status = "✅" if backup["config_backed"] else "❌"
                    table.add_row(
                        backup["name"],
                        str(backup["repos_count"]),
                        config_status,
                        backup["created"][:19] if backup["created"] != "unknown" else "unknown"
                    )
            
            console.print(table)
            console.print()  # Add spacing between tables
    
    def cleanup_old_backups(self, days: int = 30, backup_type: str = "all") -> int:
        """Clean up backups older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        backups = self.list_backups(backup_type)
        
        for backup_category, backup_list in backups.items():
            if backup_type != "all" and backup_category != backup_type:
                continue
            
            for backup in backup_list:
                try:
                    created_date = datetime.fromisoformat(backup.get("created", "1970-01-01T00:00:00"))
                    
                    if created_date < cutoff_date:
                        backup_path = Path(backup.get("file", backup.get("path", "")))
                        
                        if backup_path.exists():
                            if backup_path.is_file():
                                backup_path.unlink()
                            else:
                                shutil.rmtree(backup_path)
                            
                            # Also delete metadata if it exists
                            if backup_path.suffix == ".tar.gz":
                                metadata_path = backup_path.parent / f"{backup_path.stem}.json"
                                if metadata_path.exists():
                                    metadata_path.unlink()
                            
                            deleted_count += 1
                            console.print(f"[yellow]Deleted old backup: {backup_path.name}[/]")
                
                except Exception as e:
                    console.print(f"[red]Error deleting backup {backup.get('name', 'unknown')}: {e}[/]")
        
        if deleted_count > 0:
            console.print(f"[green]✅ Cleaned up {deleted_count} old backups[/]")
        else:
            console.print("[dim]No old backups to clean up[/]")
        
        return deleted_count
    
    def _discover_repositories(self, base_path: str = ".") -> List[str]:
        """Discover Git repositories in the filesystem"""
        repos = []
        base_path = Path(base_path).resolve()
        
        def find_repos(directory: Path, max_depth: int = 3, current_depth: int = 0):
            if current_depth > max_depth:
                return
            
            try:
                if (directory / ".git").exists():
                    repos.append(str(directory))
                    return
                
                for item in directory.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        find_repos(item, max_depth, current_depth + 1)
            except PermissionError:
                pass
        
        find_repos(base_path)
        return repos
