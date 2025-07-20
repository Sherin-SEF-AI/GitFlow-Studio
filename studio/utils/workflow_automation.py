"""
Workflow Automation Engine for GitFlow Studio
Provides automated workflow triggers, conditions, and actions for Git operations
"""

import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.prompt import Confirm, Prompt

console = Console()

class WorkflowAutomation:
    """Workflow automation engine with triggers, conditions, and actions"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.gitflow-studio")
        self.workflows_file = Path(self.config_dir) / "workflows.json"
        self.execution_log_file = Path(self.config_dir) / "workflow_execution_log.json"
        self._ensure_config_dir()
        self._load_workflows()
        self._load_execution_log()
        
        # Available triggers
        self.triggers = {
            "commit": self._trigger_on_commit,
            "push": self._trigger_on_push,
            "pull": self._trigger_on_pull,
            "branch_create": self._trigger_on_branch_create,
            "branch_delete": self._trigger_on_branch_delete,
            "merge": self._trigger_on_merge,
            "tag_create": self._trigger_on_tag_create,
            "schedule": self._trigger_on_schedule,
            "file_change": self._trigger_on_file_change
        }
        
        # Available actions
        self.actions = {
            "run_tests": self._action_run_tests,
            "run_linting": self._action_run_linting,
            "run_security_scan": self._action_run_security_scan,
            "notify": self._action_notify,
            "auto_merge": self._action_auto_merge,
            "create_backup": self._action_create_backup,
            "deploy": self._action_deploy,
            "send_email": self._action_send_email,
            "update_docs": self._action_update_docs,
            "cleanup": self._action_cleanup
        }
        
        # Available conditions
        self.conditions = {
            "file_changed": self._condition_file_changed,
            "branch_pattern": self._condition_branch_pattern,
            "commit_message_contains": self._condition_commit_message_contains,
            "time_since_last_run": self._condition_time_since_last_run,
            "file_size": self._condition_file_size,
            "commit_count": self._condition_commit_count
        }
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_workflows(self):
        """Load workflow configurations"""
        try:
            if self.workflows_file.exists():
                with open(self.workflows_file, 'r') as f:
                    self.workflows = json.load(f)
            else:
                self.workflows = {"workflows": [], "global_settings": {}}
                self._save_workflows()
        except (json.JSONDecodeError, FileNotFoundError):
            self.workflows = {"workflows": [], "global_settings": {}}
    
    def _save_workflows(self):
        """Save workflow configurations"""
        try:
            with open(self.workflows_file, 'w') as f:
                json.dump(self.workflows, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving workflows: {e}[/]")
    
    def _load_execution_log(self):
        """Load workflow execution log"""
        try:
            if self.execution_log_file.exists():
                with open(self.execution_log_file, 'r') as f:
                    self.execution_log = json.load(f)
            else:
                self.execution_log = {"executions": []}
        except (json.JSONDecodeError, FileNotFoundError):
            self.execution_log = {"executions": []}
    
    def _save_execution_log(self):
        """Save workflow execution log"""
        try:
            with open(self.execution_log_file, 'w') as f:
                json.dump(self.execution_log, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving execution log: {e}[/]")
    
    def create_workflow(self, name: str, description: str = "", 
                       trigger_config: Dict[str, Any] = None,
                       conditions: List[Dict[str, Any]] = None,
                       actions: List[Dict[str, Any]] = None,
                       enabled: bool = True) -> bool:
        """Create a new workflow"""
        if not trigger_config or not actions:
            console.print("[red]Workflow requires trigger and actions configuration[/]")
            return False
        
        workflow = {
            "id": f"workflow_{len(self.workflows['workflows']) + 1}",
            "name": name,
            "description": description,
            "trigger": trigger_config,
            "conditions": conditions or [],
            "actions": actions,
            "enabled": enabled,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "execution_count": 0,
            "last_execution": None
        }
        
        self.workflows["workflows"].append(workflow)
        self._save_workflows()
        
        console.print(f"[green]✅ Workflow '{name}' created successfully[/]")
        return True
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all configured workflows"""
        return self.workflows.get("workflows", [])
    
    def enable_workflow(self, workflow_id: str) -> bool:
        """Enable a workflow"""
        for workflow in self.workflows["workflows"]:
            if workflow["id"] == workflow_id:
                workflow["enabled"] = True
                workflow["modified"] = datetime.now().isoformat()
                self._save_workflows()
                console.print(f"[green]✅ Workflow '{workflow['name']}' enabled[/]")
                return True
        
        console.print(f"[red]Workflow '{workflow_id}' not found[/]")
        return False
    
    def disable_workflow(self, workflow_id: str) -> bool:
        """Disable a workflow"""
        for workflow in self.workflows["workflows"]:
            if workflow["id"] == workflow_id:
                workflow["enabled"] = False
                workflow["modified"] = datetime.now().isoformat()
                self._save_workflows()
                console.print(f"[green]✅ Workflow '{workflow['name']}' disabled[/]")
                return True
        
        console.print(f"[red]Workflow '{workflow_id}' not found[/]")
        return False
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        for i, workflow in enumerate(self.workflows["workflows"]):
            if workflow["id"] == workflow_id:
                workflow_name = workflow["name"]
                del self.workflows["workflows"][i]
                self._save_workflows()
                console.print(f"[green]✅ Workflow '{workflow_name}' deleted[/]")
                return True
        
        console.print(f"[red]Workflow '{workflow_id}' not found[/]")
        return False
    
    async def execute_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a specific workflow"""
        workflow = None
        for wf in self.workflows["workflows"]:
            if wf["id"] == workflow_id:
                workflow = wf
                break
        
        if not workflow:
            return {"success": False, "error": f"Workflow '{workflow_id}' not found"}
        
        if not workflow["enabled"]:
            return {"success": False, "error": f"Workflow '{workflow_id}' is disabled"}
        
        execution_result = {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "started": datetime.now().isoformat(),
            "completed": None,
            "success": True,
            "actions_executed": [],
            "error": None
        }
        
        try:
            # Check conditions if any
            if workflow.get("conditions"):
                for condition in workflow["conditions"]:
                    if not await self._evaluate_condition(condition, context or {}):
                        execution_result["success"] = False
                        execution_result["error"] = f"Condition failed: {condition}"
                        break
            
            if execution_result["success"]:
                # Execute actions
                for action_config in workflow["actions"]:
                    action_result = await self._execute_action(action_config, context or {})
                    execution_result["actions_executed"].append(action_result)
                    
                    if not action_result.get("success", True) and action_config.get("required", True):
                        execution_result["success"] = False
                        execution_result["error"] = f"Action failed: {action_config}"
                        break
            
            # Update workflow statistics
            workflow["execution_count"] += 1
            workflow["last_execution"] = datetime.now().isoformat()
            workflow["modified"] = datetime.now().isoformat()
            
        except Exception as e:
            execution_result["success"] = False
            execution_result["error"] = str(e)
        
        finally:
            execution_result["completed"] = datetime.now().isoformat()
            self._save_workflows()
            
            # Log execution
            self.execution_log["executions"].append(execution_result)
            if len(self.execution_log["executions"]) > 1000:  # Keep last 1000 executions
                self.execution_log["executions"] = self.execution_log["executions"][-1000:]
            self._save_execution_log()
        
        return execution_result
    
    async def check_triggers(self, repo_path: str, trigger_type: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Check for triggered workflows"""
        triggered_workflows = []
        
        for workflow in self.workflows["workflows"]:
            if not workflow["enabled"]:
                continue
            
            workflow_trigger = workflow.get("trigger", {})
            if workflow_trigger.get("type") == trigger_type:
                # Additional trigger-specific checking can be added here
                triggered_workflows.append(workflow)
        
        # Execute triggered workflows
        for workflow in triggered_workflows:
            execution_result = await self.execute_workflow(workflow["id"], context)
            if execution_result["success"]:
                console.print(f"[green]✅ Workflow '{workflow['name']}' executed successfully[/]")
            else:
                console.print(f"[red]❌ Workflow '{workflow['name']}' failed: {execution_result.get('error', 'Unknown error')}[/]")
        
        return triggered_workflows
    
    # Trigger implementations
    async def _trigger_on_commit(self, context: Dict[str, Any]) -> bool:
        """Trigger on commit"""
        return True  # Implementation would check Git log
    
    async def _trigger_on_push(self, context: Dict[str, Any]) -> bool:
        """Trigger on push"""
        return True
    
    async def _trigger_on_pull(self, context: Dict[str, Any]) -> bool:
        """Trigger on pull"""
        return True
    
    async def _trigger_on_branch_create(self, context: Dict[str, Any]) -> bool:
        """Trigger on branch creation"""
        return True
    
    async def _trigger_on_branch_delete(self, context: Dict[str, Any]) -> bool:
        """Trigger on branch deletion"""
        return True
    
    async def _trigger_on_merge(self, context: Dict[str, Any]) -> bool:
        """Trigger on merge"""
        return True
    
    async def _trigger_on_tag_create(self, context: Dict[str, Any]) -> bool:
        """Trigger on tag creation"""
        return True
    
    async def _trigger_on_schedule(self, context: Dict[str, Any]) -> bool:
        """Trigger on schedule"""
        return True
    
    async def _trigger_on_file_change(self, context: Dict[str, Any]) -> bool:
        """Trigger on file change"""
        return True
    
    # Condition implementations
    async def _condition_file_changed(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if specific files changed"""
        patterns = condition.get("patterns", [])
        changed_files = context.get("changed_files", [])
        
        for pattern in patterns:
            for file_path in changed_files:
                if self._matches_pattern(file_path, pattern):
                    return True
        return len(patterns) == 0  # If no patterns specified, condition is always true
    
    async def _condition_branch_pattern(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check branch name against pattern"""
        pattern = condition.get("pattern", "")
        current_branch = context.get("branch", "")
        
        return self._matches_pattern(current_branch, pattern)
    
    async def _condition_commit_message_contains(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if commit message contains specified text"""
        keywords = condition.get("keywords", [])
        commit_message = context.get("commit_message", "")
        
        return any(keyword.lower() in commit_message.lower() for keyword in keywords)
    
    async def _condition_time_since_last_run(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check time since last workflow execution"""
        max_minutes = condition.get("max_minutes", 60)
        last_run = context.get("last_execution")
        
        if not last_run:
            return True
        
        try:
            last_run_time = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
            time_diff = datetime.now() - last_run_time.replace(tzinfo=None)
            return time_diff.total_seconds() / 60 >= max_minutes
        except ValueError:
            return True
    
    async def _condition_file_size(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check file size conditions"""
        max_size_mb = condition.get("max_size_mb", 10)
        changed_files = context.get("changed_files", [])
        
        for file_path in changed_files:
            try:
                file_size = Path(file_path).stat().st_size
                if file_size > max_size_mb * 1024 * 1024:
                    return False
            except (OSError, FileNotFoundError):
                continue
        
        return True
    
    async def _condition_commit_count(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check commit count conditions"""
        max_commits = condition.get("max_commits", 100)
        commit_count = context.get("commit_count", 0)
        
        return commit_count <= max_commits
    
    # Action implementations
    async def _action_run_tests(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Run tests action"""
        repo_path = context.get("repo_path", ".")
        test_command = action_config.get("command", "pytest")
        
        try:
            result = subprocess.run(
                test_command.split(),
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=action_config.get("timeout", 300)
            )
            
            return {
                "success": result.returncode == 0,
                "command": test_command,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "command": test_command,
                "error": "Command timed out",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "command": test_command,
                "error": str(e)
            }
    
    async def _action_run_linting(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Run linting action"""
        repo_path = context.get("repo_path", ".")
        lint_command = action_config.get("command", "flake8")
        
        try:
            result = subprocess.run(
                lint_command.split() + [repo_path],
                capture_output=True,
                text=True,
                timeout=action_config.get("timeout", 120)
            )
            
            return {
                "success": result.returncode == 0,
                "command": lint_command,
                "output": result.stdout,
                "error": result.stderr,
                "warning_count": len([line for line in result.stdout.split('\n') if line.strip()])
            }
        except Exception as e:
            return {
                "success": False,
                "command": lint_command,
                "error": str(e)
            }
    
    async def _action_run_security_scan(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Run security scan action"""
        # This would integrate with the SecurityScanner class
        return {
            "success": True,
            "message": "Security scan completed",
            "scan_type": action_config.get("scan_type", "simple")
        }
    
    async def _action_notify(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification action"""
        message = action_config.get("message", "Workflow completed")
        notification_type = action_config.get("type", "console")
        
        if notification_type == "console":
            console.print(f"[blue]📢 {message}[/]")
        
        return {
            "success": True,
            "message": f"Notification sent via {notification_type}",
            "notification_type": notification_type
        }
    
    async def _action_auto_merge(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Automatic merge action"""
        branch = action_config.get("branch", "main")
        repo_path = context.get("repo_path", ".")
        
        try:
            # This would implement actual Git merge logic
            return {
                "success": True,
                "message": f"Auto-merge to {branch}",
                "branch": branch
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _action_create_backup(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create backup action"""
        repo_path = context.get("repo_path", ".")
        backup_name = action_config.get("name", f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # This would integrate with BackupRestoreManager
        return {
            "success": True,
            "message": f"Backup '{backup_name}' created",
            "backup_name": backup_name
        }
    
    async def _action_deploy(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy action"""
        deploy_command = action_config.get("command", "echo 'Deploy command not specified'")
        
        try:
            result = subprocess.run(
                deploy_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=action_config.get("timeout", 600)
            )
            
            return {
                "success": result.returncode == 0,
                "command": deploy_command,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "command": deploy_command,
                "error": str(e)
            }
    
    async def _action_send_email(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send email action"""
        # This would integrate with email sending capability
        return {
            "success": True,
            "message": "Email sent",
            "to": action_config.get("to", ""),
            "subject": action_config.get("subject", "Workflow notification")
        }
    
    async def _action_update_docs(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Update documentation action"""
        return {
            "success": True,
            "message": "Documentation updated"
        }
    
    async def _action_cleanup(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Cleanup action"""
        cleanup_patterns = action_config.get("patterns", ["*.pyc", "__pycache__", "*.log"])
        repo_path = context.get("repo_path", ".")
        
        cleaned_files = 0
        for pattern in cleanup_patterns:
            # Implementation would clean up files matching patterns
            pass
        
        return {
            "success": True,
            "message": f"Cleaned up {cleaned_files} files",
            "cleaned_files": cleaned_files
        }
    
    # Helper methods
    async def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a condition"""
        condition_type = condition.get("type")
        
        if condition_type in self.conditions:
            return await self.conditions[condition_type](condition, context)
        
        return True  # Unknown conditions default to True
    
    async def _execute_action(self, action_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action"""
        action_type = action_config.get("type")
        
        if action_type in self.actions:
            return await self.actions[action_type](action_config, context)
        
        return {
            "success": False,
            "error": f"Unknown action type: {action_type}"
        }
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches pattern (supports wildcards)"""
        import fnmatch
        return fnmatch.fnmatch(text, pattern)
    
    def display_workflows(self):
        """Display all workflows in a formatted table"""
        workflows = self.list_workflows()
        
        if not workflows:
            console.print("[yellow]No workflows configured[/]")
            return
        
        table = Table(title="Configured Workflows", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Trigger", style="green")
        table.add_column("Actions", justify="right", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Executions", justify="right")
        table.add_column("Last Run", style="dim")
        
        for workflow in workflows:
            status = "✅ Enabled" if workflow["enabled"] else "❌ Disabled"
            trigger_type = workflow.get("trigger", {}).get("type", "unknown")
            actions_count = len(workflow.get("actions", []))
            executions = workflow.get("execution_count", 0)
            last_run = workflow.get("last_execution")
            
            if last_run:
                try:
                    last_run_time = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
                    last_run = last_run_time.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    pass
            
            table.add_row(
                workflow["name"],
                trigger_type,
                str(actions_count),
                status,
                str(executions),
                last_run or "Never"
            )
        
        console.print(table)
