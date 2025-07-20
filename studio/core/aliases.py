"""
Custom aliases system for GitFlow Studio
Allows users to create shortcuts for frequently used commands
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

class AliasManager:
    """Manages custom aliases for GitFlow Studio commands"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.gitflow-studio")
        self.aliases_file = Path(self.config_dir) / "aliases.json"
        self.aliases: Dict[str, Dict[str, Any]] = {}
        self._ensure_config_dir()
        self._load_aliases()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_aliases(self):
        """Load aliases from JSON file"""
        try:
            if self.aliases_file.exists():
                with open(self.aliases_file, 'r') as f:
                    self.aliases = json.load(f)
            else:
                self.aliases = {}
                self._save_aliases()
        except Exception as e:
            console.print(f"[red]Error loading aliases: {e}[/]")
            self.aliases = {}
    
    def _save_aliases(self):
        """Save aliases to JSON file"""
        try:
            with open(self.aliases_file, 'w') as f:
                json.dump(self.aliases, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving aliases: {e}[/]")
    
    def add_alias(self, name: str, command: str, description: str = "", tags: List[str] = None) -> bool:
        """Add a new alias"""
        if not name or not command:
            console.print("[red]Alias name and command are required![/]")
            return False
        
        if name in self.aliases:
            console.print(f"[yellow]Alias '{name}' already exists. Use --force to overwrite.[/]")
            return False
        
        self.aliases[name] = {
            "command": command,
            "description": description,
            "tags": tags or [],
            "created_at": str(Path().stat().st_mtime),
            "usage_count": 0
        }
        
        self._save_aliases()
        console.print(f"[green]✅ Alias '{name}' created successfully![/]")
        return True
    
    def remove_alias(self, name: str) -> bool:
        """Remove an alias"""
        if name not in self.aliases:
            console.print(f"[red]Alias '{name}' not found![/]")
            return False
        
        del self.aliases[name]
        self._save_aliases()
        console.print(f"[green]✅ Alias '{name}' removed successfully![/]")
        return True
    
    def list_aliases(self, filter_tags: List[str] = None, show_usage: bool = False):
        """List all aliases in a formatted table"""
        if not self.aliases:
            console.print(Panel("[yellow]No aliases found. Create your first alias with 'alias add'[/]", 
                              title="[blue]Aliases", border_style="blue"))
            return
        
        table = Table(
            title="[bold blue]Custom Aliases[/]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="blue"
        )
        
        table.add_column("Alias", style="cyan", no_wrap=True)
        table.add_column("Command", style="white")
        table.add_column("Description", style="green")
        table.add_column("Tags", style="yellow")
        
        if show_usage:
            table.add_column("Usage Count", style="blue", justify="right")
        
        filtered_aliases = self.aliases
        if filter_tags:
            filtered_aliases = {
                name: alias for name, alias in self.aliases.items()
                if any(tag in alias.get("tags", []) for tag in filter_tags)
            }
        
        for name, alias_data in filtered_aliases.items():
            command = alias_data.get("command", "")
            description = alias_data.get("description", "")
            tags = ", ".join(alias_data.get("tags", []))
            
            row = [name, command, description, tags]
            if show_usage:
                usage_count = alias_data.get("usage_count", 0)
                row.append(str(usage_count))
            
            table.add_row(*row)
        
        console.print(table)
    
    def get_alias(self, name: str) -> Optional[str]:
        """Get the command for an alias"""
        if name in self.aliases:
            # Increment usage count
            self.aliases[name]["usage_count"] = self.aliases[name].get("usage_count", 0) + 1
            self._save_aliases()
            return self.aliases[name]["command"]
        return None
    
    def search_aliases(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Search aliases by name, description, or tags"""
        results = {}
        query_lower = query.lower()
        
        for name, alias_data in self.aliases.items():
            if (query_lower in name.lower() or
                query_lower in alias_data.get("description", "").lower() or
                any(query_lower in tag.lower() for tag in alias_data.get("tags", []))):
                results[name] = alias_data
        
        return results
    
    def export_aliases(self, format: str = "json", file_path: Optional[str] = None) -> bool:
        """Export aliases to file"""
        if format not in ["json", "csv"]:
            console.print("[red]Unsupported format. Use 'json' or 'csv'[/]")
            return False
        
        if not file_path:
            file_path = f"aliases_export.{format}"
        
        try:
            if format == "json":
                with open(file_path, 'w') as f:
                    json.dump(self.aliases, f, indent=2)
            elif format == "csv":
                import csv
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Alias", "Command", "Description", "Tags", "Usage Count"])
                    for name, data in self.aliases.items():
                        writer.writerow([
                            name,
                            data.get("command", ""),
                            data.get("description", ""),
                            ", ".join(data.get("tags", [])),
                            data.get("usage_count", 0)
                        ])
            
            console.print(f"[green]✅ Aliases exported to {file_path}[/]")
            return True
        except Exception as e:
            console.print(f"[red]Error exporting aliases: {e}[/]")
            return False
    
    def import_aliases(self, file_path: str, overwrite: bool = False) -> bool:
        """Import aliases from file"""
        try:
            with open(file_path, 'r') as f:
                imported_aliases = json.load(f)
            
            imported_count = 0
            skipped_count = 0
            
            for name, alias_data in imported_aliases.items():
                if name in self.aliases and not overwrite:
                    skipped_count += 1
                    continue
                
                self.aliases[name] = alias_data
                imported_count += 1
            
            self._save_aliases()
            console.print(f"[green]✅ Imported {imported_count} aliases[/]")
            if skipped_count > 0:
                console.print(f"[yellow]⚠️ Skipped {skipped_count} existing aliases (use --overwrite to force)[/]")
            return True
        except Exception as e:
            console.print(f"[red]Error importing aliases: {e}[/]")
            return False
    
    def get_most_used_aliases(self, limit: int = 10) -> List[tuple]:
        """Get most frequently used aliases"""
        sorted_aliases = sorted(
            self.aliases.items(),
            key=lambda x: x[1].get("usage_count", 0),
            reverse=True
        )
        return sorted_aliases[:limit]
    
    def get_alias_stats(self) -> Dict[str, Any]:
        """Get statistics about aliases"""
        total_aliases = len(self.aliases)
        total_usage = sum(alias.get("usage_count", 0) for alias in self.aliases.values())
        avg_usage = total_usage / total_aliases if total_aliases > 0 else 0
        
        # Count tags
        tag_counts = {}
        for alias in self.aliases.values():
            for tag in alias.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            "total_aliases": total_aliases,
            "total_usage": total_usage,
            "average_usage": round(avg_usage, 2),
            "tag_counts": tag_counts,
            "most_used": self.get_most_used_aliases(5)
        } 