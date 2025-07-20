"""
Performance monitoring system for GitFlow Studio
Tracks tool performance metrics and provides insights
"""

import time
import psutil
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from functools import wraps

console = Console()

class PerformanceMonitor:
    """Monitors and tracks performance metrics for GitFlow Studio"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.gitflow-studio")
        self.metrics_file = Path(self.config_dir) / "performance_metrics.json"
        self.metrics: Dict[str, Any] = {
            "operations": {},
            "memory_usage": [],
            "cpu_usage": [],
            "git_operations": {},
            "startup_time": None,
            "total_operations": 0
        }
        self._ensure_config_dir()
        self._load_metrics()
        self.start_time = time.time()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_metrics(self):
        """Load performance metrics from file"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    self.metrics = json.load(f)
        except Exception as e:
            console.print(f"[red]Error loading performance metrics: {e}[/]")
    
    def _save_metrics(self):
        """Save performance metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
        except Exception as e:
            console.print(f"[red]Error saving performance metrics: {e}[/]")
    
    def monitor_operation(self, operation_name: str):
        """Decorator to monitor operation performance"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                start_cpu = psutil.cpu_percent()
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                except Exception as e:
                    success = False
                    raise e
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss
                    end_cpu = psutil.cpu_percent()
                    
                    duration = end_time - start_time
                    memory_delta = end_memory - start_memory
                    cpu_avg = (start_cpu + end_cpu) / 2
                    
                    self._record_operation(operation_name, duration, memory_delta, cpu_avg, success)
                
                return result
            return wrapper
        return decorator
    
    def _record_operation(self, operation_name: str, duration: float, memory_delta: int, 
                         cpu_usage: float, success: bool):
        """Record operation performance metrics"""
        if operation_name not in self.metrics["operations"]:
            self.metrics["operations"][operation_name] = {
                "count": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "min_duration": float('inf'),
                "max_duration": 0,
                "total_memory": 0,
                "avg_memory": 0,
                "total_cpu": 0,
                "avg_cpu": 0,
                "success_count": 0,
                "error_count": 0,
                "last_execution": None
            }
        
        op_metrics = self.metrics["operations"][operation_name]
        op_metrics["count"] += 1
        op_metrics["total_duration"] += duration
        op_metrics["avg_duration"] = op_metrics["total_duration"] / op_metrics["count"]
        op_metrics["min_duration"] = min(op_metrics["min_duration"], duration)
        op_metrics["max_duration"] = max(op_metrics["max_duration"], duration)
        op_metrics["total_memory"] += memory_delta
        op_metrics["avg_memory"] = op_metrics["total_memory"] / op_metrics["count"]
        op_metrics["total_cpu"] += cpu_usage
        op_metrics["avg_cpu"] = op_metrics["total_cpu"] / op_metrics["count"]
        op_metrics["last_execution"] = datetime.now().isoformat()
        
        if success:
            op_metrics["success_count"] += 1
        else:
            op_metrics["error_count"] += 1
        
        self.metrics["total_operations"] += 1
        self._save_metrics()
    
    def record_git_operation(self, operation: str, repo_path: str, duration: float, 
                           success: bool, additional_data: Dict[str, Any] = None):
        """Record Git operation performance"""
        if operation not in self.metrics["git_operations"]:
            self.metrics["git_operations"][operation] = {
                "count": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "success_count": 0,
                "error_count": 0,
                "repositories": {},
                "last_execution": None
            }
        
        git_metrics = self.metrics["git_operations"][operation]
        git_metrics["count"] += 1
        git_metrics["total_duration"] += duration
        git_metrics["avg_duration"] = git_metrics["total_duration"] / git_metrics["count"]
        git_metrics["last_execution"] = datetime.now().isoformat()
        
        if success:
            git_metrics["success_count"] += 1
        else:
            git_metrics["error_count"] += 1
        
        # Track per-repository metrics
        if repo_path not in git_metrics["repositories"]:
            git_metrics["repositories"][repo_path] = {
                "count": 0,
                "total_duration": 0,
                "avg_duration": 0
            }
        
        repo_metrics = git_metrics["repositories"][repo_path]
        repo_metrics["count"] += 1
        repo_metrics["total_duration"] += duration
        repo_metrics["avg_duration"] = repo_metrics["total_duration"] / repo_metrics["count"]
        
        self._save_metrics()
    
    def record_memory_usage(self):
        """Record current memory usage"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            memory_data = {
                "timestamp": datetime.now().isoformat(),
                "rss": memory_info.rss,
                "vms": memory_info.vms,
                "percent": process.memory_percent(),
                "available": psutil.virtual_memory().available
            }
            
            self.metrics["memory_usage"].append(memory_data)
            
            # Keep only last 1000 records
            if len(self.metrics["memory_usage"]) > 1000:
                self.metrics["memory_usage"] = self.metrics["memory_usage"][-1000:]
            
            self._save_metrics()
        except Exception as e:
            console.print(f"[red]Error recording memory usage: {e}[/]")
    
    def record_cpu_usage(self):
        """Record current CPU usage"""
        try:
            cpu_data = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(),
                "process_cpu_percent": psutil.Process().cpu_percent()
            }
            
            self.metrics["cpu_usage"].append(cpu_data)
            
            # Keep only last 1000 records
            if len(self.metrics["cpu_usage"]) > 1000:
                self.metrics["cpu_usage"] = self.metrics["cpu_usage"][-1000:]
            
            self._save_metrics()
        except Exception as e:
            console.print(f"[red]Error recording CPU usage: {e}[/]")
    
    def get_operation_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Get operation performance statistics"""
        if operation_name:
            return self.metrics["operations"].get(operation_name, {})
        
        return self.metrics["operations"]
    
    def get_git_operation_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get Git operation performance statistics"""
        if operation:
            return self.metrics["git_operations"].get(operation, {})
        
        return self.metrics["git_operations"]
    
    def get_memory_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get memory usage statistics for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_memory = [
            m for m in self.metrics["memory_usage"]
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        if not recent_memory:
            return {}
        
        rss_values = [m["rss"] for m in recent_memory]
        vms_values = [m["vms"] for m in recent_memory]
        percent_values = [m["percent"] for m in recent_memory]
        
        return {
            "count": len(recent_memory),
            "avg_rss": sum(rss_values) / len(rss_values),
            "max_rss": max(rss_values),
            "min_rss": min(rss_values),
            "avg_vms": sum(vms_values) / len(vms_values),
            "max_vms": max(vms_values),
            "min_vms": min(vms_values),
            "avg_percent": sum(percent_values) / len(percent_values),
            "max_percent": max(percent_values),
            "min_percent": min(percent_values)
        }
    
    def get_cpu_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get CPU usage statistics for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_cpu = [
            c for c in self.metrics["cpu_usage"]
            if datetime.fromisoformat(c["timestamp"]) > cutoff_time
        ]
        
        if not recent_cpu:
            return {}
        
        cpu_percent_values = [c["cpu_percent"] for c in recent_cpu]
        process_cpu_values = [c["process_cpu_percent"] for c in recent_cpu]
        
        return {
            "count": len(recent_cpu),
            "avg_cpu_percent": sum(cpu_percent_values) / len(cpu_percent_values),
            "max_cpu_percent": max(cpu_percent_values),
            "min_cpu_percent": min(cpu_percent_values),
            "avg_process_cpu": sum(process_cpu_values) / len(process_cpu_values),
            "max_process_cpu": max(process_cpu_values),
            "min_process_cpu": min(process_cpu_values)
        }
    
    def display_performance_summary(self):
        """Display overall performance summary"""
        total_ops = self.metrics["total_operations"]
        operations = self.metrics["operations"]
        
        if not operations:
            console.print(Panel("[yellow]No performance data available.[/]", 
                              title="[blue]Performance Summary", border_style="blue"))
            return
        
        # Calculate overall stats
        total_duration = sum(op["total_duration"] for op in operations.values())
        total_success = sum(op["success_count"] for op in operations.values())
        total_errors = sum(op["error_count"] for op in operations.values())
        avg_duration = total_duration / total_ops if total_ops > 0 else 0
        
        # Get most used operations
        most_used = sorted(operations.items(), key=lambda x: x[1]["count"], reverse=True)[:5]
        
        # Get slowest operations
        slowest_ops = sorted(operations.items(), key=lambda x: x[1]["avg_duration"], reverse=True)[:5]
        
        table = Table(
            title="[bold blue]Performance Summary[/]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="blue"
        )
        
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Total Operations", str(total_ops))
        table.add_row("Total Duration", f"{total_duration:.2f}s")
        table.add_row("Average Duration", f"{avg_duration:.3f}s")
        table.add_row("Success Rate", f"{(total_success/total_ops*100):.1f}%" if total_ops > 0 else "0%")
        table.add_row("Error Rate", f"{(total_errors/total_ops*100):.1f}%" if total_ops > 0 else "0%")
        
        console.print(table)
        
        # Most used operations
        if most_used:
            console.print("\n[bold]Most Used Operations:[/]")
            for op_name, op_data in most_used:
                console.print(f"  {op_name}: {op_data['count']} times (avg: {op_data['avg_duration']:.3f}s)")
        
        # Slowest operations
        if slowest_ops:
            console.print("\n[bold]Slowest Operations:[/]")
            for op_name, op_data in slowest_ops:
                console.print(f"  {op_name}: {op_data['avg_duration']:.3f}s avg ({op_data['count']} times)")
    
    def display_operation_details(self, operation_name: str):
        """Display detailed performance for a specific operation"""
        if operation_name not in self.metrics["operations"]:
            console.print(f"[red]Operation '{operation_name}' not found in metrics.[/]")
            return
        
        op_data = self.metrics["operations"][operation_name]
        
        table = Table(
            title=f"[bold blue]Operation Details: {operation_name}[/]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="blue"
        )
        
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Total Executions", str(op_data["count"]))
        table.add_row("Success Count", str(op_data["success_count"]))
        table.add_row("Error Count", str(op_data["error_count"]))
        table.add_row("Success Rate", f"{(op_data['success_count']/op_data['count']*100):.1f}%")
        table.add_row("Total Duration", f"{op_data['total_duration']:.2f}s")
        table.add_row("Average Duration", f"{op_data['avg_duration']:.3f}s")
        table.add_row("Min Duration", f"{op_data['min_duration']:.3f}s")
        table.add_row("Max Duration", f"{op_data['max_duration']:.3f}s")
        table.add_row("Average Memory", f"{op_data['avg_memory']/1024/1024:.1f} MB")
        table.add_row("Average CPU", f"{op_data['avg_cpu']:.1f}%")
        table.add_row("Last Execution", op_data.get("last_execution", "Never"))
        
        console.print(table)
    
    def display_system_stats(self):
        """Display current system performance statistics"""
        try:
            # Current memory usage
            memory = psutil.virtual_memory()
            process_memory = psutil.Process().memory_info()
            
            # Current CPU usage
            cpu_percent = psutil.cpu_percent()
            process_cpu = psutil.Process().cpu_percent()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            table = Table(
                title="[bold blue]System Performance[/]",
                show_header=True,
                header_style="bold magenta",
                box=box.ROUNDED,
                border_style="blue"
            )
            
            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")
            
            table.add_row("System Memory Used", f"{memory.percent:.1f}%")
            table.add_row("System Memory Available", f"{memory.available/1024/1024/1024:.1f} GB")
            table.add_row("Process Memory (RSS)", f"{process_memory.rss/1024/1024:.1f} MB")
            table.add_row("Process Memory (VMS)", f"{process_memory.vms/1024/1024:.1f} MB")
            table.add_row("System CPU Usage", f"{cpu_percent:.1f}%")
            table.add_row("Process CPU Usage", f"{process_cpu:.1f}%")
            table.add_row("Disk Usage", f"{disk.percent:.1f}%")
            table.add_row("Disk Free", f"{disk.free/1024/1024/1024:.1f} GB")
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error getting system stats: {e}[/]")
    
    def export_performance_data(self, format: str = "json", filename: Optional[str] = None) -> str:
        """Export performance data to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_data_{timestamp}.{format}"
        
        file_path = Path.cwd() / filename
        
        try:
            if format.lower() == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.metrics, f, indent=2, default=str)
            elif format.lower() == "csv":
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Operation", "Count", "Avg Duration", "Success Rate", "Avg Memory", "Avg CPU"])
                    
                    for op_name, op_data in self.metrics["operations"].items():
                        success_rate = (op_data["success_count"] / op_data["count"] * 100) if op_data["count"] > 0 else 0
                        writer.writerow([
                            op_name,
                            op_data["count"],
                            f"{op_data['avg_duration']:.3f}",
                            f"{success_rate:.1f}%",
                            f"{op_data['avg_memory']/1024/1024:.1f} MB",
                            f"{op_data['avg_cpu']:.1f}%"
                        ])
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            console.print(f"[green]✅ Performance data exported to {file_path}[/]")
            return str(file_path)
        except Exception as e:
            console.print(f"[red]Error exporting performance data: {e}[/]")
            return ""
    
    def cleanup_old_metrics(self, days: int = 30):
        """Clean up old performance metrics"""
        cutoff_time = datetime.now() - timedelta(days=days)
        cutoff_timestamp = cutoff_time.isoformat()
        
        # Clean up memory usage
        self.metrics["memory_usage"] = [
            m for m in self.metrics["memory_usage"]
            if m["timestamp"] > cutoff_timestamp
        ]
        
        # Clean up CPU usage
        self.metrics["cpu_usage"] = [
            c for c in self.metrics["cpu_usage"]
            if c["timestamp"] > cutoff_timestamp
        ]
        
        self._save_metrics()
        console.print(f"[green]✅ Cleaned up performance metrics older than {days} days[/]")
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        self.metrics = {
            "operations": {},
            "memory_usage": [],
            "cpu_usage": [],
            "git_operations": {},
            "startup_time": None,
            "total_operations": 0
        }
        self._save_metrics()
        console.print("[green]✅ Performance metrics reset[/]") 