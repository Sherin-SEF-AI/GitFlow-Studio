"""
Security Scanner for GitFlow Studio
Provides comprehensive security scanning including vulnerability detection, secrets scanning, and security best practices
"""

import os
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.tree import Tree

console = Console()

class SecurityScanner:
    """Comprehensive security scanner for repositories and configurations"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.gitflow-studio")
        self.secret_patterns = self._load_secret_patterns()
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.security_rules = self._load_security_rules()
    
    def _load_secret_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for detecting secrets and sensitive information"""
        return {
            "api_keys": [
                r'(?i)api[_-]?key["\s]*[:=]["\s]*["\']?([a-zA-Z0-9_-]{20,})["\']?',
                r'(?i)apikey["\s]*[:=]["\s]*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            ],
            "passwords": [
                r'(?i)password["\s]*[:=]["\s]*["\']?([^\s"\']+)["\']?',
                r'(?i)passwd["\s]*[:=]["\s]*["\']?([^\s"\']+)["\']?',
                r'(?i)pwd["\s]*[:=]["\s]*["\']?([^\s"\']+)["\']?',
            ],
            "tokens": [
                r'(?i)token["\s]*[:=]["\s]*["\']?([a-zA-Z0-9._-]{20,})["\']?',
                r'(?i)bearer["\s]+([a-zA-Z0-9._-]{20,})',
            ],
            "secrets": [
                r'(?i)secret["\s]*[:=]["\s]*["\']?([a-zA-Z0-9._-]{20,})["\']?',
                r'(?i)private[_-]?key["\s]*[:=]["\s]*["\']?(-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----)["\']?',
            ],
            "database_credentials": [
                r'(?i)database[_-]?url["\s]*[:=]["\s]*["\']?(mongodb|postgres|mysql)://[^"\'\s]+["\']?',
                r'(?i)db[_-]?(pass|password|pwd)["\s]*[:=]["\s]*["\']?([^\s"\']+)["\']?',
            ],
            "aws_credentials": [
                r'AKIA[0-9A-Z]{16}',
                r'(?i)aws[_-]?access[_-]?key[_-]?id["\s]*[:=]["\s]*["\']?(AKIA[0-9A-Z]{16})["\']?',
                r'(?i)aws[_-]?secret[_-]?access[_-]?key["\s]*[:=]["\s]*["\']?([A-Za-z0-9/+=]{40})["\']?',
            ],
            "github_tokens": [
                r'ghp_[a-zA-Z0-9]{36}',
                r'gho_[a-zA-Z0-9]{36}',
                r'ghu_[a-zA-Z0-9]{36}',
                r'ghs_[a-zA-Z0-9]{36}',
                r'ghr_[a-zA-Z0-9]{36}',
            ],
            "slack_tokens": [
                r'xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}',
            ],
            "stripe_keys": [
                r'sk_live_[0-9a-zA-Z]{24}',
                r'pk_live_[0-9a-zA-Z]{24}',
                r'sk_test_[0-9a-zA-Z]{24}',
                r'pk_test_[0-9a-zA-Z]{24}',
            ]
        }
    
    def _load_vulnerability_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for detecting common security vulnerabilities"""
        return {
            "sql_injection": [
                r'SELECT.*FROM.*%s',  # String formatting in SQL
                r'INSERT.*INTO.*%s',
                r'UPDATE.*SET.*%s',
                r'DELETE.*FROM.*%s',
                r'execute.*%',
                r'cursor\.execute\(.*\+.*\)',  # String concatenation in SQL
            ],
            "command_injection": [
                r'os\.system\(.*\+',  # String concatenation in os.system
                r'subprocess\.call\(.*\+',
                r'eval\(',
                r'exec\(',
                r'__import__\(',
            ],
            "path_traversal": [
                r'open\(.*\.\./',  # Directory traversal
                r'file\(.*\.\./',
                r'Path\(.*\.\./',
            ],
            "xss": [
                r'innerHTML\s*=\s*[^;]*\+',
                r'document\.write\(.*\+',
                r'\.html\(.*\+',
            ],
            "insecure_random": [
                r'random\.random\(\)',
                r'os\.urandom\(4\)',
                r'hashlib\.md5\(',
            ]
        }
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """Load security configuration rules"""
        return {
            "permissions": {
                "world_writable_files": True,
                "setuid_files": True,
                "insecure_permissions": True
            },
            "dependencies": {
                "check_vulnerabilities": True,
                "check_outdated": True,
                "check_licenses": True
            },
            "files": {
                "check_env_files": True,
                "check_config_files": True,
                "check_log_files": True
            }
        }
    
    def scan_secrets(self, repo_path: str, custom_patterns: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Scan repository for secrets and sensitive information"""
        repo_path = Path(repo_path)
        findings = {category: [] for category in self.secret_patterns.keys()}
        findings["custom"] = []
        
        # Add custom patterns if provided
        if custom_patterns:
            for pattern in custom_patterns:
                findings["custom"].append({"pattern": pattern})
        
        # Files to exclude from scanning
        exclude_patterns = [
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            '.venv', 'venv', 'env', '.env', '*.pyc', '*.log'
        ]
        
        scanned_files = 0
        total_size = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning for secrets...", total=None)
            
            for file_path in repo_path.rglob('*'):
                if file_path.is_file() and not any(pattern in str(file_path) for pattern in exclude_patterns):
                    try:
                        # Skip binary files
                        if not self._is_text_file(file_path):
                            continue
                        
                        file_size = file_path.stat().st_size
                        if file_size > 1024 * 1024:  # Skip files larger than 1MB
                            continue
                        
                        scanned_files += 1
                        total_size += file_size
                        
                        progress.update(task, description=f"Scanning {file_path.name}...")
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            line_num = 0
                            
                            for line in content.split('\n'):
                                line_num += 1
                                
                                # Check against all secret patterns
                                for category, patterns in self.secret_patterns.items():
                                    for pattern in patterns:
                                        matches = re.finditer(pattern, line, re.IGNORECASE)
                                        for match in matches:
                                            findings[category].append({
                                                "file": str(file_path.relative_to(repo_path)),
                                                "line": line_num,
                                                "content": line.strip(),
                                                "match": match.group(),
                                                "severity": self._get_severity_level(category, match.group()),
                                                "category": category,
                                                "pattern": pattern
                                            })
                        
                        # Check custom patterns
                        if custom_patterns:
                            for pattern in custom_patterns:
                                matches = re.finditer(pattern, line, re.IGNORECASE)
                                for match in matches:
                                    findings["custom"].append({
                                        "file": str(file_path.relative_to(repo_path)),
                                        "line": line_num,
                                        "content": line.strip(),
                                        "match": match.group(),
                                        "severity": "medium",
                                        "category": "custom",
                                        "pattern": pattern
                                    })
                    
                    except (UnicodeDecodeError, PermissionError, OSError):
                        continue
        
        # Add summary
        findings["_summary"] = {
            "scanned_files": scanned_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "scan_time": datetime.now().isoformat(),
            "total_findings": sum(len(findings[cat]) for cat in self.secret_patterns.keys()) + len(findings["custom"])
        }
        
        return findings
    
    def scan_vulnerabilities(self, repo_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Scan repository for common security vulnerabilities in code"""
        repo_path = Path(repo_path)
        findings = {category: [] for category in self.vulnerability_patterns.keys()}
        
        # Supported file extensions for vulnerability scanning
        supported_extensions = {'.py', '.js', '.ts', '.java', '.php', '.rb', '.go', '.rs'}
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        line_num = 0
                        
                        for line in content.split('\n'):
                            line_num += 1
                            
                            for vuln_type, patterns in self.vulnerability_patterns.items():
                                for pattern in patterns:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        findings[vuln_type].append({
                                            "file": str(file_path.relative_to(repo_path)),
                                            "line": line_num,
                                            "content": line.strip(),
                                            "severity": self._get_vuln_severity(vuln_type),
                                            "type": vuln_type,
                                            "pattern": pattern
                                        })
                
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        return findings
    
    def scan_dependencies(self, repo_path: str) -> Dict[str, Any]:
        """Scan for vulnerable dependencies"""
        repo_path = Path(repo_path)
        results = {
            "vulnerabilities": [],
            "outdated": [],
            "license_issues": [],
            "total_dependencies": 0
        }
        
        # Check Python dependencies
        if (repo_path / "requirements.txt").exists():
            python_results = self._scan_python_dependencies(repo_path)
            results["vulnerabilities"].extend(python_results.get("vulnerabilities", []))
            results["outdated"].extend(python_results.get("outdated", []))
            results["total_dependencies"] += python_results.get("total", 0)
        
        # Check Node.js dependencies
        if (repo_path / "package.json").exists():
            node_results = self._scan_nodejs_dependencies(repo_path)
            results["vulnerabilities"].extend(node_results.get("vulnerabilities", []))
            results["outdated"].extend(node_results.get("outdated", []))
            results["total_dependencies"] += node_results.get("total", 0)
        
        return results
    
    def _scan_python_dependencies(self, repo_path: Path) -> Dict[str, Any]:
        """Scan Python dependencies for vulnerabilities"""
        results = {"vulnerabilities": [], "outdated": [], "total": 0}
        
        try:
            # Try using safety for vulnerability scanning
            safety_result = subprocess.run(
                ["safety", "check", "--json"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if safety_result.returncode == 0 and safety_result.stdout:
                try:
                    vulnerabilities = json.loads(safety_result.stdout)
                    results["vulnerabilities"] = vulnerabilities
                except json.JSONDecodeError:
                    pass
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            # Check for outdated packages
            pip_result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if pip_result.returncode == 0 and pip_result.stdout:
                try:
                    outdated = json.loads(pip_result.stdout)
                    results["outdated"] = outdated
                    results["total"] = len(outdated)
                except json.JSONDecodeError:
                    pass
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return results
    
    def _scan_nodejs_dependencies(self, repo_path: Path) -> Dict[str, Any]:
        """Scan Node.js dependencies for vulnerabilities"""
        results = {"vulnerabilities": [], "outdated": [], "total": 0}
        
        try:
            # Try using npm audit
            audit_result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if audit_result.returncode != 0 and audit_result.stdout:  # npm audit returns non-zero on findings
                try:
                    audit_data = json.loads(audit_result.stdout)
                    if "vulnerabilities" in audit_data:
                        for pkg, vuln_data in audit_data["vulnerabilities"].items():
                            results["vulnerabilities"].append({
                                "package": pkg,
                                "severity": vuln_data.get("severity", "unknown"),
                                "vulnerabilities": vuln_data
                            })
                except json.JSONDecodeError:
                    pass
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return results
    
    def scan_file_permissions(self, repo_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Scan for insecure file permissions"""
        repo_path = Path(repo_path)
        findings = {
            "world_writable": [],
            "setuid": [],
            "insecure_permissions": []
        }
        
        try:
            # Find world-writable files
            find_result = subprocess.run(
                ["find", str(repo_path), "-type", "f", "-perm", "-002"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if find_result.returncode == 0:
                for file_path in find_result.stdout.strip().split('\n'):
                    if file_path.strip():
                        stat_result = subprocess.run(
                            ["stat", "-c", "%n %a %U %G", file_path],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        if stat_result.returncode == 0:
                            parts = stat_result.stdout.strip().split()
                            if len(parts) >= 4:
                                findings["world_writable"].append({
                                    "file": file_path,
                                    "permissions": parts[1],
                                    "owner": parts[2],
                                    "group": parts[3]
                                })
            
            # Find setuid/setgid files
            find_result = subprocess.run(
                ["find", str(repo_path), "-type", "f", "\\(-perm -4000 -o -perm -2000\\)"],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )
            
            if find_result.returncode == 0:
                for file_path in find_result.stdout.strip().split('\n'):
                    if file_path.strip():
                        findings["setuid"].append({"file": file_path})
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return findings
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely to be a text file"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return not b'\x00' in chunk
        except:
            return False
    
    def _get_severity_level(self, category: str, match: str) -> str:
        """Determine severity level for secret findings"""
        high_severity_categories = ["aws_credentials", "github_tokens", "slack_tokens", "stripe_keys"]
        if category in high_severity_categories:
            return "high"
        elif category in ["api_keys", "tokens", "secrets"]:
            return "medium"
        else:
            return "low"
    
    def _get_vuln_severity(self, vuln_type: str) -> str:
        """Determine severity level for vulnerability findings"""
        high_severity = ["sql_injection", "command_injection"]
        medium_severity = ["path_traversal", "xss"]
        
        if vuln_type in high_severity:
            return "high"
        elif vuln_type in medium_severity:
            return "medium"
        else:
            return "low"
    
    def comprehensive_scan(self, repo_path: str) -> Dict[str, Any]:
        """Perform comprehensive security scan"""
        console.print(f"[blue]Starting comprehensive security scan for {Path(repo_path).name}...[/]")
        
        scan_results = {
            "repository": str(repo_path),
            "scan_time": datetime.now().isoformat(),
            "secrets": {},
            "vulnerabilities": {},
            "dependencies": {},
            "permissions": {},
            "summary": {}
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Security scanning...", total=100)
            
            # Scan for secrets
            progress.update(task, description="Scanning for secrets...", completed=20)
            scan_results["secrets"] = self.scan_secrets(repo_path)
            
            # Scan for vulnerabilities
            progress.update(task, description="Scanning for vulnerabilities...", completed=40)
            scan_results["vulnerabilities"] = self.scan_vulnerabilities(repo_path)
            
            # Scan dependencies
            progress.update(task, description="Scanning dependencies...", completed=60)
            scan_results["dependencies"] = self.scan_dependencies(repo_path)
            
            # Scan file permissions
            progress.update(task, description="Scanning file permissions...", completed=80)
            scan_results["permissions"] = self.scan_file_permissions(repo_path)
            
            progress.update(task, completed=100, description="Security scan completed!")
        
        # Generate summary
        total_secrets = sum(len(scan_results["secrets"].get(cat, [])) for cat in self.secret_patterns.keys())
        total_vulns = sum(len(scan_results["vulnerabilities"].get(cat, [])) for cat in self.vulnerability_patterns.keys())
        total_dep_vulns = len(scan_results["dependencies"].get("vulnerabilities", []))
        total_perms = (len(scan_results["permissions"].get("world_writable", [])) + 
                      len(scan_results["permissions"].get("setuid", [])))
        
        scan_results["summary"] = {
            "secrets_found": total_secrets,
            "vulnerabilities_found": total_vulns,
            "dependency_vulnerabilities": total_dep_vulns,
            "permission_issues": total_perms,
            "total_issues": total_secrets + total_vulns + total_dep_vulns + total_perms,
            "risk_level": self._calculate_risk_level(total_secrets, total_vulns, total_dep_vulns, total_perms)
        }
        
        return scan_results
    
    def _calculate_risk_level(self, secrets: int, vulns: int, dep_vulns: int, perms: int) -> str:
        """Calculate overall risk level"""
        score = secrets * 3 + vulns * 2 + dep_vulns * 1 + perms * 1
        
        if score >= 10:
            return "HIGH"
        elif score >= 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def display_security_report(self, scan_results: Dict[str, Any]):
        """Display comprehensive security report"""
        summary = scan_results.get("summary", {})
        risk_level = summary.get("risk_level", "UNKNOWN")
        
        # Overall risk assessment
        risk_color = "red" if risk_level == "HIGH" else "yellow" if risk_level == "MEDIUM" else "green"
        
        console.print(Panel(
            f"[bold]Security Risk Level: [{risk_color}]{risk_level}[/{risk_color}][/bold]\n"
            f"Total Issues Found: {summary.get('total_issues', 0)}\n"
            f"Secrets: {summary.get('secrets_found', 0)} | "
            f"Vulnerabilities: {summary.get('vulnerabilities_found', 0)} | "
            f"Dependency Issues: {summary.get('dependency_vulnerabilities', 0)} | "
            f"Permission Issues: {summary.get('permission_issues', 0)}",
            title="Security Scan Summary",
            border_style=risk_color
        ))
        
        # Secrets findings
        secrets = scan_results.get("secrets", {})
        if any(len(secrets.get(cat, [])) > 0 for cat in self.secret_patterns.keys()):
            console.print(Panel(
                f"[red]🚨 CRITICAL: Secrets detected in repository![/red]",
                title="Secret Detection",
                border_style="red"
            ))
            
            table = Table(title="Secret Findings", box=box.ROUNDED)
            table.add_column("Category", style="cyan")
            table.add_column("File", style="green")
            table.add_column("Line", justify="right")
            table.add_column("Severity", style="yellow")
            
            for category, findings in secrets.items():
                if category.startswith("_") or not findings:
                    continue
                for finding in findings[:5]:  # Show first 5 findings per category
                    table.add_row(
                        finding.get("category", category),
                        Path(finding.get("file", "")).name,
                        str(finding.get("line", "")),
                        finding.get("severity", "unknown").upper()
                    )
            
            console.print(table)
        
        # Vulnerability findings
        vulns = scan_results.get("vulnerabilities", {})
        if any(len(vulns.get(cat, [])) > 0 for cat in self.vulnerability_patterns.keys()):
            console.print(Panel(
                f"[yellow]⚠️ Code vulnerabilities detected[/yellow]",
                title="Vulnerability Detection",
                border_style="yellow"
            ))
        
        # Dependency vulnerabilities
        deps = scan_results.get("dependencies", {})
        if deps.get("vulnerabilities"):
            console.print(Panel(
                f"[yellow]Found {len(deps['vulnerabilities'])} dependency vulnerabilities[/yellow]",
                title="Dependency Security",
                border_style="yellow"
            ))
