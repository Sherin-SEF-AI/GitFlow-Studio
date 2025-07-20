"""
Export functionality for GitFlow Studio
Allows users to export analytics data in JSON/CSV formats
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class ExportManager:
    """Manages data export functionality for GitFlow Studio"""
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or Path.cwd() / "exports"
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure output directory exists"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def export_repository_stats(self, stats: Dict[str, Any], format: str = "json", 
                               filename: Optional[str] = None) -> str:
        """Export repository statistics"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"repo_stats_{timestamp}.{format}"
        
        file_path = Path(self.output_dir) / filename
        
        try:
            if format.lower() == "json":
                self._export_json(stats, file_path)
            elif format.lower() == "csv":
                self._export_csv_stats(stats, file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            console.print(f"[green]✅ Repository stats exported to {file_path}[/]")
            return str(file_path)
        except Exception as e:
            console.print(f"[red]Error exporting repository stats: {e}[/]")
            return ""
    
    def export_commit_activity(self, activity: List[Dict[str, Any]], format: str = "json",
                              filename: Optional[str] = None) -> str:
        """Export commit activity data"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"commit_activity_{timestamp}.{format}"
        
        file_path = Path(self.output_dir) / filename
        
        try:
            if format.lower() == "json":
                self._export_json(activity, file_path)
            elif format.lower() == "csv":
                self._export_csv_activity(activity, file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            console.print(f"[green]✅ Commit activity exported to {file_path}[/]")
            return str(file_path)
        except Exception as e:
            console.print(f"[red]Error exporting commit activity: {e}[/]")
            return ""
    
    def export_file_changes(self, changes: List[Dict[str, Any]], format: str = "json",
                           filename: Optional[str] = None) -> str:
        """Export file change statistics"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"file_changes_{timestamp}.{format}"
        
        file_path = Path(self.output_dir) / filename
        
        try:
            if format.lower() == "json":
                self._export_json(changes, file_path)
            elif format.lower() == "csv":
                self._export_csv_file_changes(changes, file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            console.print(f"[green]✅ File changes exported to {file_path}[/]")
            return str(file_path)
        except Exception as e:
            console.print(f"[red]Error exporting file changes: {e}[/]")
            return ""
    
    def export_branch_activity(self, activity: List[Dict[str, Any]], format: str = "json",
                              filename: Optional[str] = None) -> str:
        """Export branch activity data"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"branch_activity_{timestamp}.{format}"
        
        file_path = Path(self.output_dir) / filename
        
        try:
            if format.lower() == "json":
                self._export_json(activity, file_path)
            elif format.lower() == "csv":
                self._export_csv_branch_activity(activity, file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            console.print(f"[green]✅ Branch activity exported to {file_path}[/]")
            return str(file_path)
        except Exception as e:
            console.print(f"[red]Error exporting branch activity: {e}[/]")
            return ""
    
    def export_contributor_stats(self, stats: List[Dict[str, Any]], format: str = "json",
                                filename: Optional[str] = None) -> str:
        """Export contributor statistics"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"contributor_stats_{timestamp}.{format}"
        
        file_path = Path(self.output_dir) / filename
        
        try:
            if format.lower() == "json":
                self._export_json(stats, file_path)
            elif format.lower() == "csv":
                self._export_csv_contributor_stats(stats, file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            console.print(f"[green]✅ Contributor stats exported to {file_path}[/]")
            return str(file_path)
        except Exception as e:
            console.print(f"[red]Error exporting contributor stats: {e}[/]")
            return ""
    
    def export_repository_health(self, health: Dict[str, Any], format: str = "json",
                                filename: Optional[str] = None) -> str:
        """Export repository health data"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"repo_health_{timestamp}.{format}"
        
        file_path = Path(self.output_dir) / filename
        
        try:
            if format.lower() == "json":
                self._export_json(health, file_path)
            elif format.lower() == "csv":
                self._export_csv_health(health, file_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            console.print(f"[green]✅ Repository health exported to {file_path}[/]")
            return str(file_path)
        except Exception as e:
            console.print(f"[red]Error exporting repository health: {e}[/]")
            return ""
    
    def export_all_analytics(self, analytics_data: Dict[str, Any], format: str = "json",
                            filename: Optional[str] = None) -> List[str]:
        """Export all analytics data in one operation"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"all_analytics_{timestamp}.{format}"
        
        exported_files = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Exporting analytics data...", total=len(analytics_data))
            
            for data_type, data in analytics_data.items():
                progress.update(task, description=f"Exporting {data_type}...")
                
                if data_type == "stats":
                    file_path = self.export_repository_stats(data, format, f"{filename}_{data_type}.{format}")
                elif data_type == "activity":
                    file_path = self.export_commit_activity(data, format, f"{filename}_{data_type}.{format}")
                elif data_type == "files":
                    file_path = self.export_file_changes(data, format, f"{filename}_{data_type}.{format}")
                elif data_type == "branches":
                    file_path = self.export_branch_activity(data, format, f"{filename}_{data_type}.{format}")
                elif data_type == "contributors":
                    file_path = self.export_contributor_stats(data, format, f"{filename}_{data_type}.{format}")
                elif data_type == "health":
                    file_path = self.export_repository_health(data, format, f"{filename}_{data_type}.{format}")
                else:
                    # Generic export for unknown data types
                    file_path = self._export_generic(data, data_type, format, f"{filename}_{data_type}.{format}")
                
                if file_path:
                    exported_files.append(file_path)
                
                progress.advance(task)
        
        console.print(f"[green]✅ Exported {len(exported_files)} analytics files[/]")
        return exported_files
    
    def _export_json(self, data: Any, file_path: Path):
        """Export data to JSON format"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _export_csv_stats(self, stats: Dict[str, Any], file_path: Path):
        """Export repository stats to CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            
            for key, value in stats.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        writer.writerow([f"{key}.{sub_key}", sub_value])
                else:
                    writer.writerow([key, value])
    
    def _export_csv_activity(self, activity: List[Dict[str, Any]], file_path: Path):
        """Export commit activity to CSV"""
        if not activity:
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Get all possible keys from the data
            all_keys = set()
            for item in activity:
                all_keys.update(item.keys())
            
            headers = sorted(all_keys)
            writer.writerow(headers)
            
            for item in activity:
                row = [item.get(key, "") for key in headers]
                writer.writerow(row)
    
    def _export_csv_file_changes(self, changes: List[Dict[str, Any]], file_path: Path):
        """Export file changes to CSV"""
        if not changes:
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["File", "Changes", "Additions", "Deletions", "Last Modified"])
            
            for change in changes:
                writer.writerow([
                    change.get("file", ""),
                    change.get("changes", 0),
                    change.get("additions", 0),
                    change.get("deletions", 0),
                    change.get("last_modified", "")
                ])
    
    def _export_csv_branch_activity(self, activity: List[Dict[str, Any]], file_path: Path):
        """Export branch activity to CSV"""
        if not activity:
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Branch", "Commits", "Last Commit", "Status", "Age"])
            
            for branch in activity:
                writer.writerow([
                    branch.get("name", ""),
                    branch.get("commits", 0),
                    branch.get("last_commit", ""),
                    branch.get("status", ""),
                    branch.get("age", "")
                ])
    
    def _export_csv_contributor_stats(self, stats: List[Dict[str, Any]], file_path: Path):
        """Export contributor stats to CSV"""
        if not stats:
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Contributor", "Commits", "Additions", "Deletions", "First Commit", "Last Commit"])
            
            for contributor in stats:
                writer.writerow([
                    contributor.get("name", ""),
                    contributor.get("commits", 0),
                    contributor.get("additions", 0),
                    contributor.get("deletions", 0),
                    contributor.get("first_commit", ""),
                    contributor.get("last_commit", "")
                ])
    
    def _export_csv_health(self, health: Dict[str, Any], file_path: Path):
        """Export repository health to CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value", "Status"])
            
            for key, value in health.items():
                if isinstance(value, dict):
                    status = value.get("status", "")
                    actual_value = value.get("value", value)
                    writer.writerow([key, actual_value, status])
                else:
                    writer.writerow([key, value, ""])
    
    def _export_generic(self, data: Any, data_type: str, format: str, filename: str) -> str:
        """Generic export for unknown data types"""
        file_path = Path(self.output_dir) / filename
        
        try:
            if format.lower() == "json":
                self._export_json(data, file_path)
            else:
                # For CSV, try to flatten the data
                if isinstance(data, list) and data:
                    self._export_csv_generic(data, file_path)
                else:
                    self._export_json(data, file_path)
            
            return str(file_path)
        except Exception as e:
            console.print(f"[red]Error exporting {data_type}: {e}[/]")
            return ""
    
    def _export_csv_generic(self, data: List[Dict[str, Any]], file_path: Path):
        """Generic CSV export for list of dictionaries"""
        if not data:
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Get all possible keys from the data
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())
            
            headers = sorted(all_keys)
            writer.writerow(headers)
            
            for item in data:
                row = [item.get(key, "") for key in headers]
                writer.writerow(row)
    
    def list_exports(self) -> List[Dict[str, Any]]:
        """List all exported files"""
        exports = []
        
        for file_path in Path(self.output_dir).glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                exports.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "type": file_path.suffix[1:] if file_path.suffix else "unknown"
                })
        
        return sorted(exports, key=lambda x: x["modified"], reverse=True)
    
    def show_exports(self):
        """Display exported files in a table"""
        exports = self.list_exports()
        
        if not exports:
            console.print(Panel("[yellow]No exported files found.[/]", 
                              title="[blue]Exports", border_style="blue"))
            return
        
        table = Table(
            title="[bold blue]Exported Files[/]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="blue"
        )
        
        table.add_column("Filename", style="cyan", no_wrap=True)
        table.add_column("Type", style="yellow")
        table.add_column("Size", style="green", justify="right")
        table.add_column("Modified", style="white")
        
        for export in exports:
            size_str = self._format_file_size(export["size"])
            modified_str = export["modified"].strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                export["filename"],
                export["type"].upper(),
                size_str,
                modified_str
            )
        
        console.print(table)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def cleanup_exports(self, days_old: int = 30) -> int:
        """Clean up old export files"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        for file_path in Path(self.output_dir).glob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    console.print(f"[red]Error deleting {file_path}: {e}[/]")
        
        if deleted_count > 0:
            console.print(f"[green]✅ Cleaned up {deleted_count} old export files[/]")
        else:
            console.print("[yellow]No old export files to clean up[/]")
        
        return deleted_count 