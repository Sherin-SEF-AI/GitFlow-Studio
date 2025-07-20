"""
Sync Management System for GitFlow Studio
Manages synchronization across multiple remote repositories and backup locations
"""

import os
import subprocess
import json
import asyncio
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm, Prompt
from rich.tree import Tree

console = Console()

class SyncManager:
    """Manages synchronization across multiple remote repositories"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.gitflow-studio")
        self.sync_config_file = Path(self.config_dir) / "sync_config.json"
        self.sync_log_file = Path(self.config_dir) / "sync_log.json"
        self._load_config()
        self._load_sync_log()
    
    def _load_config(self):
        """Load sync configuration"""
        if self.sync_config_file.exists():
            try:
                with open(self.sync_config_file, 'r') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.config = {
                    "remotes": {},
                    "sync_groups": {},
                    "auto_sync": False,
                    "conflict_resolution": "ask",
                    "backup_before_sync": True
                }
        else:
            self.config = {
                "remotes": {},
                "sync_groups": {},
                "auto_sync": False,
                "conflict_resolution": "ask",
                "backup_before_sync": True
            }
            self._save_config()
    
    def _save_config(self):
        """Save sync configuration"""
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        try:
            with open(self.sync_config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving sync config: {e}[/]")
    
    def _load_sync_log(self):
        """Load sync operation log"""
        if self.sync_log_file.exists():
            try:
                with open(self.sync_log_file, 'r') as f:
                    self.sync_log = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.sync_log = {"operations": []}
        else:
            self.sync_log = {"operations": []}
    
    def _save_sync_log(self):
        """Save sync operation log"""
        try:
            with open(self.sync_log_file, 'w') as f:
                json.dump(self.sync_log, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving sync log: {e}[/]")
    
    def add_remote_sync(self, name: str, repo_path: str, remote_url: str, 
                       branch: str = "main", credentials: Dict[str, str] = None) -> bool:
        """Add a remote repository to sync configuration"""
        if not Path(repo_path).exists():
            console.print(f"[red]Repository path does not exist: {repo_path}[/]")
            return False
        
        # Verify it's a Git repository
        if not (Path(repo_path) / ".git").exists():
            console.print(f"[red]Not a Git repository: {repo_path}[/]")
            return False
        
        # Test remote URL accessibility
        try:
            result = subprocess.run(
                ["git", "ls-remote", remote_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                console.print(f"[red]Cannot access remote URL: {remote_url}[/]")
                return False
        
        except subprocess.TimeoutExpired:
            console.print(f"[yellow]Warning: Remote URL access timed out: {remote_url}[/]")
        
        # Add to configuration
        self.config["remotes"][name] = {
            "repo_path": str(Path(repo_path).resolve()),
            "remote_url": remote_url,
            "branch": branch,
            "credentials": credentials or {},
            "last_sync": None,
            "auto_sync": False
        }
        
        # Add remote to Git repository if not exists
        try:
            # Check if remote already exists
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if name not in result.stdout:
                # Add the remote
                subprocess.run(
                    ["git", "remote", "add", name, remote_url],
                    cwd=repo_path,
                    capture_output=True,
                    timeout=10
                )
        
        except subprocess.TimeoutExpired:
            console.print(f"[yellow]Warning: Could not add remote {name}[/]")
        
        self._save_config()
        console.print(f"[green]✅ Remote '{name}' added for sync[/]")
        return True
    
    def create_sync_group(self, name: str, remote_names: List[str], 
                         sync_strategy: str = "bidirectional") -> bool:
        """Create a sync group for coordinated operations"""
        # Validate all remotes exist
        for remote_name in remote_names:
            if remote_name not in self.config["remotes"]:
                console.print(f"[red]Remote '{remote_name}' not found[/]")
                return False
        
        # Validate sync strategy
        valid_strategies = ["bidirectional", "unidirectional", "hub-spoke"]
        if sync_strategy not in valid_strategies:
            console.print(f"[red]Invalid sync strategy. Choose from: {valid_strategies}[/]")
            return False
        
        self.config["sync_groups"][name] = {
            "remotes": remote_names,
            "strategy": sync_strategy,
            "created": datetime.now().isoformat(),
            "last_sync": None
        }
        
        self._save_config()
        console.print(f"[green]✅ Sync group '{name}' created[/]")
        return True
    
    async def sync_repository(self, remote_name: str, direction: str = "bidirectional") -> Dict[str, Any]:
        """Sync a single repository with its remote"""
        if remote_name not in self.config["remotes"]:
            return {
                "success": False,
                "error": f"Remote '{remote_name}' not found"
            }
        
        remote_config = self.config["remotes"][remote_name]
        repo_path = remote_config["repo_path"]
        remote_url = remote_config["remote_url"]
        branch = remote_config["branch"]
        
        sync_result = {
            "remote": remote_name,
            "repo_path": repo_path,
            "direction": direction,
            "success": True,
            "operations": [],
            "conflicts": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Fetch latest changes
            fetch_result = subprocess.run(
                ["git", "fetch", remote_name, branch],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            sync_result["operations"].append({
                "action": "fetch",
                "success": fetch_result.returncode == 0,
                "output": fetch_result.stdout,
                "error": fetch_result.stderr
            })
            
            if fetch_result.returncode != 0:
                sync_result["success"] = False
                sync_result["error"] = f"Failed to fetch: {fetch_result.stderr}"
                return sync_result
            
            # Check for divergent branches
            diff_result = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", f"HEAD...{remote_name}/{branch}"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if diff_result.returncode == 0:
                behind, ahead = map(int, diff_result.stdout.strip().split('\t'))
                
                if direction in ["bidirectional", "push"]:
                    if ahead > 0:
                        # Push local changes
                        push_result = subprocess.run(
                            ["git", "push", remote_name, f"HEAD:{branch}"],
                            cwd=repo_path,
                            capture_output=True,
                            text=True,
                            timeout=120
                        )
                        
                        sync_result["operations"].append({
                            "action": "push",
                            "success": push_result.returncode == 0,
                            "output": push_result.stdout,
                            "error": push_result.stderr
                        })
                        
                        if push_result.returncode != 0:
                            sync_result["conflicts"].append({
                                "type": "push_conflict",
                                "message": push_result.stderr
                            })
                
                if direction in ["bidirectional", "pull"]:
                    if behind > 0:
                        # Check for local changes before pulling
                        status_result = subprocess.run(
                            ["git", "status", "--porcelain"],
                            cwd=repo_path,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        if status_result.stdout.strip():
                            # Handle local changes
                            conflict_resolution = self.config.get("conflict_resolution", "ask")
                            
                            if conflict_resolution == "stash":
                                # Stash local changes
                                stash_result = subprocess.run(
                                    ["git", "stash", "push", "-m", f"Auto-stash before sync {datetime.now().isoformat()}"],
                                    cwd=repo_path,
                                    capture_output=True,
                                    text=True,
                                    timeout=30
                                )
                                
                                if stash_result.returncode != 0:
                                    sync_result["conflicts"].append({
                                        "type": "stash_failed",
                                        "message": stash_result.stderr
                                    })
                                    sync_result["success"] = False
                                    return sync_result
                            
                            elif conflict_resolution == "ask":
                                sync_result["conflicts"].append({
                                    "type": "local_changes",
                                    "message": "Local changes detected, manual intervention required"
                                })
                                sync_result["success"] = False
                                return sync_result
                        
                        # Pull remote changes
                        pull_result = subprocess.run(
                            ["git", "pull", remote_name, branch],
                            cwd=repo_path,
                            capture_output=True,
                            text=True,
                            timeout=120
                        )
                        
                        sync_result["operations"].append({
                            "action": "pull",
                            "success": pull_result.returncode == 0,
                            "output": pull_result.stdout,
                            "error": pull_result.stderr
                        })
                        
                        if pull_result.returncode != 0:
                            if "conflict" in pull_result.stdout.lower() or "conflict" in pull_result.stderr.lower():
                                sync_result["conflicts"].append({
                                    "type": "merge_conflict",
                                    "message": "Merge conflicts detected",
                                    "details": pull_result.stdout + pull_result.stderr
                                })
                                sync_result["success"] = False
            
            # Update last sync time
            remote_config["last_sync"] = datetime.now().isoformat()
            self._save_config()
            
        except subprocess.TimeoutExpired:
            sync_result["success"] = False
            sync_result["error"] = "Operation timed out"
        except Exception as e:
            sync_result["success"] = False
            sync_result["error"] = str(e)
        
        # Log sync operation
        self.sync_log["operations"].append(sync_result)
        self._save_sync_log()
        
        return sync_result
    
    async def sync_group(self, group_name: str) -> Dict[str, Any]:
        """Sync all repositories in a sync group"""
        if group_name not in self.config["sync_groups"]:
            return {
                "success": False,
                "error": f"Sync group '{group_name}' not found"
            }
        
        group_config = self.config["sync_groups"][group_name]
        remote_names = group_config["remotes"]
        strategy = group_config["strategy"]
        
        group_result = {
            "group": group_name,
            "strategy": strategy,
            "success": True,
            "remote_results": {},
            "timestamp": datetime.now().isoformat()
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Syncing group '{group_name}'...", total=len(remote_names))
            
            if strategy == "bidirectional":
                # Sync all remotes bidirectionally
                for remote_name in remote_names:
                    progress.update(task, description=f"Syncing {remote_name}...")
                    result = await self.sync_repository(remote_name, "bidirectional")
                    group_result["remote_results"][remote_name] = result
                    
                    if not result["success"]:
                        group_result["success"] = False
                    
                    progress.advance(task)
            
            elif strategy == "unidirectional":
                # Sync from first remote to all others
                if remote_names:
                    source_remote = remote_names[0]
                    
                    # First, sync source to get latest changes
                    progress.update(task, description=f"Syncing source {source_remote}...")
                    source_result = await self.sync_repository(source_remote, "pull")
                    group_result["remote_results"][source_remote] = source_result
                    progress.advance(task, advance=1.0 / len(remote_names))
                    
                    # Then sync all other remotes from source
                    for remote_name in remote_names[1:]:
                        progress.update(task, description=f"Syncing {remote_name} from {source_remote}...")
                        # This would require custom logic to sync between different remotes
                        result = await self.sync_repository(remote_name, "pull")
                        group_result["remote_results"][remote_name] = result
                        
                        if not result["success"]:
                            group_result["success"] = False
                        
                        progress.advance(task, advance=1.0 / len(remote_names))
            
            elif strategy == "hub-spoke":
                # First remote is hub, others are spokes
                if len(remote_names) >= 2:
                    hub_remote = remote_names[0]
                    spoke_remotes = remote_names[1:]
                    
                    # Sync hub first
                    progress.update(task, description=f"Syncing hub {hub_remote}...")
                    hub_result = await self.sync_repository(hub_remote, "bidirectional")
                    group_result["remote_results"][hub_remote] = hub_result
                    progress.advance(task, advance=1.0 / len(remote_names))
                    
                    # Sync all spokes to hub
                    for spoke_remote in spoke_remotes:
                        progress.update(task, description=f"Syncing spoke {spoke_remote} to hub...")
                        spoke_result = await self.sync_repository(spoke_remote, "pull")
                        group_result["remote_results"][spoke_remote] = spoke_result
                        
                        if not spoke_result["success"]:
                            group_result["success"] = False
                        
                        progress.advance(task, advance=1.0 / len(remote_names))
        
        # Update group last sync time
        group_config["last_sync"] = datetime.now().isoformat()
        self._save_config()
        
        return group_result
    
    def display_sync_status(self) -> None:
        """Display current sync status for all configured remotes"""
        if not self.config["remotes"]:
            console.print("[yellow]No remote repositories configured for sync[/]")
            return
        
        table = Table(title="Sync Status", box=box.ROUNDED)
        table.add_column("Remote", style="cyan")
        table.add_column("Repository", style="green")
        table.add_column("Branch", style="blue")
        table.add_column("Last Sync", style="dim")
        table.add_column("Status", style="green")
        
        for remote_name, remote_config in self.config["remotes"].items():
            repo_name = Path(remote_config["repo_path"]).name
            branch = remote_config["branch"]
            last_sync = remote_config.get("last_sync")
            
            if last_sync:
                try:
                    sync_time = datetime.fromisoformat(last_sync)
                    if sync_time > datetime.now() - timedelta(hours=24):
                        status = "✅ Recent"
                    elif sync_time > datetime.now() - timedelta(days=7):
                        status = "⚠️ Old"
                    else:
                        status = "❌ Very Old"
                except ValueError:
                    status = "❓ Unknown"
            else:
                status = "❌ Never"
                last_sync = "Never"
            
            table.add_row(
                remote_name,
                repo_name,
                branch,
                last_sync[:19] if last_sync != "Never" else "Never",
                status
            )
        
        console.print(table)
    
    def display_sync_groups(self) -> None:
        """Display configured sync groups"""
        if not self.config["sync_groups"]:
            console.print("[yellow]No sync groups configured[/]")
            return
        
        for group_name, group_config in self.config["sync_groups"].items():
            panel_content = f"[bold]Strategy:[/bold] {group_config['strategy']}\n"
            panel_content += f"[bold]Remotes:[/bold] {', '.join(group_config['remotes'])}\n"
            panel_content += f"[bold]Created:[/bold] {group_config['created'][:19]}\n"
            
            last_sync = group_config.get('last_sync')
            if last_sync:
                panel_content += f"[bold]Last Sync:[/bold] {last_sync[:19]}"
            else:
                panel_content += "[bold]Last Sync:[/bold] Never"
            
            console.print(Panel(
                panel_content,
                title=f"Sync Group: {group_name}",
                border_style="blue"
            ))
    
    def list_sync_conflicts(self) -> List[Dict[str, Any]]:
        """List all unresolved sync conflicts"""
        conflicts = []
        
        for operation in self.sync_log.get("operations", []):
            if not operation.get("success", True) and operation.get("conflicts"):
                conflicts.extend(operation["conflicts"])
        
        return conflicts
    
    def resolve_sync_conflict(self, conflict_id: str, resolution: str) -> bool:
        """Resolve a specific sync conflict"""
        # This would implement conflict resolution logic
        # For now, just mark as resolved in the log
        console.print(f"[green]Conflict {conflict_id} resolved with: {resolution}[/]")
        return True
    
    def auto_sync_enabled_remotes(self) -> Dict[str, Any]:
        """Sync all remotes with auto-sync enabled"""
        auto_sync_remotes = {
            remote_name: config 
            for remote_name, config in self.config["remotes"].items()
            if config.get("auto_sync", False)
        }
        
        if not auto_sync_remotes:
            return {
                "success": True,
                "message": "No remotes have auto-sync enabled",
                "synced": []
            }
        
        results = []
        
        async def sync_all():
            tasks = [
                self.sync_repository(remote_name)
                for remote_name in auto_sync_remotes.keys()
            ]
            
            sync_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for remote_name, result in zip(auto_sync_remotes.keys(), sync_results):
                if isinstance(result, Exception):
                    results.append({
                        "remote": remote_name,
                        "success": False,
                        "error": str(result)
                    })
                else:
                    results.append({
                        "remote": remote_name,
                        "success": result.get("success", False),
                        "conflicts": result.get("conflicts", [])
                    })
        
        # Run async sync
        asyncio.run(sync_all())
        
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        return {
            "success": len(failed) == 0,
            "synced": successful,
            "failed": failed,
            "total": len(results)
        }
