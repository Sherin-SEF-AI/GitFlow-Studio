"""
Code Quality Analyzer for GitFlow Studio
Provides code quality analysis, linting integration, and best practices checking
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax

console = Console()

class CodeQualityAnalyzer:
    """Analyzes code quality and integrates with various linting tools"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.gitflow-studio")
        self.quality_cache = Path(self.config_dir) / "quality_cache.json"
        self._load_config()
    
    def _load_config(self):
        """Load code quality configuration"""
        self.config = {
            "python": {
                "enabled_tools": ["flake8", "black", "pylint", "mypy"],
                "flake8_config": {
                    "max_line_length": 88,
                    "extend_ignore": ["E203", "W503"],
                    "max_complexity": 10
                },
                "black_config": {
                    "line_length": 88,
                    "target_version": ["py39"]
                }
            },
            "javascript": {
                "enabled_tools": ["eslint", "prettier"],
                "eslint_config": {
                    "preset": "recommended"
                }
            },
            "general": {
                "check_secrets": True,
                "check_dependencies": True,
                "check_documentation": True
            }
        }
    
    def detect_language(self, file_path: Path) -> str:
        """Detect programming language based on file extension"""
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala'
        }
        
        extension = file_path.suffix.lower()
        return extensions.get(extension, 'unknown')
    
    def check_dependencies(self, repo_path: str) -> Dict[str, Any]:
        """Check for dependency vulnerabilities and updates"""
        repo_path = Path(repo_path)
        results = {
            "vulnerabilities": [],
            "outdated": [],
            "security_score": 100
        }
        
        # Check Python dependencies
        requirements_files = [
            repo_path / "requirements.txt",
            repo_path / "requirements-dev.txt",
            repo_path / "pyproject.toml",
            repo_path / "setup.py",
            repo_path / "Pipfile"
        ]
        
        for req_file in requirements_files:
            if req_file.exists():
                try:
                    # Use safety for security check if available
                    safety_result = subprocess.run(
                        ["safety", "check", "-r", str(req_file), "--json"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if safety_result.returncode == 0 and safety_result.stdout:
                        vulnerabilities = json.loads(safety_result.stdout)
                        results["vulnerabilities"].extend(vulnerabilities)
                
                except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                    pass
        
        # Adjust security score based on vulnerabilities
        if results["vulnerabilities"]:
            results["security_score"] = max(0, 100 - len(results["vulnerabilities"]) * 10)
        
        return results
    
    def analyze_file_complexity(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file complexity"""
        language = self.detect_language(file_path)
        complexity_score = 0
        issues = []
        
        if language == 'python':
            try:
                # Use radon for Python complexity analysis
                result = subprocess.run(
                    ["radon", "cc", str(file_path), "--json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout:
                    data = json.loads(result.stdout)
                    file_name = str(file_path)
                    
                    if file_name in data:
                        for function_data in data[file_name]:
                            complexity = function_data.get('complexity', 1)
                            if complexity > 10:
                                issues.append({
                                    "function": function_data.get('name', 'unknown'),
                                    "complexity": complexity,
                                    "line": function_data.get('lineno', 0),
                                    "severity": "high" if complexity > 15 else "medium"
                                })
                        
                        # Calculate average complexity
                        if data[file_name]:
                            avg_complexity = sum(f.get('complexity', 1) for f in data[file_name]) / len(data[file_name])
                            complexity_score = min(100, max(0, 100 - (avg_complexity - 1) * 10))
        
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                pass
        
        return {
            "complexity_score": complexity_score,
            "issues": issues,
            "language": language
        }
    
    def check_secrets(self, repo_path: str, patterns: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Check for potential secrets in the repository"""
        if patterns is None:
            patterns = [
                r'(?i)password\s*[:=]\s*["\']?[^\s"\']+["\']?',
                r'(?i)api[_-]?key\s*[:=]\s*["\']?[^\s"\']+["\']?',
                r'(?i)secret\s*[:=]\s*["\']?[^\s"\']+["\']?',
                r'(?i)token\s*[:=]\s*["\']?[^\s"\']+["\']?',
                r'-----BEGIN (RSA )?PRIVATE KEY-----',
                r'sk_live_[0-9a-zA-Z]{24}',
                r'AIza[0-9A-Za-z\\-_]{35}'
            ]
        
        repo_path = Path(repo_path)
        secrets_found = []
        
        # Files to exclude from secret scanning
        exclude_patterns = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', '.env']
        
        try:
            import re
            
            for file_path in repo_path.rglob('*'):
                if file_path.is_file() and not any(pattern in str(file_path) for pattern in exclude_patterns):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            line_num = 0
                            
                            for line in content.split('\n'):
                                line_num += 1
                                
                                for pattern in patterns:
                                    if re.search(pattern, line):
                                        secrets_found.append({
                                            "file": str(file_path.relative_to(repo_path)),
                                            "line": line_num,
                                            "line_content": line.strip(),
                                            "pattern": pattern,
                                            "severity": "high"
                                        })
                    except (UnicodeDecodeError, PermissionError):
                        continue
        
        except Exception as e:
            console.print(f"[yellow]Warning: Error scanning for secrets: {e}[/]")
        
        return {"secrets": secrets_found}
    
    def run_linting(self, repo_path: str, language: str = None) -> Dict[str, Any]:
        """Run linting tools on the repository"""
        repo_path = Path(repo_path)
        linting_results = {
            "language": language or "auto",
            "tools_used": [],
            "issues": [],
            "score": 100
        }
        
        if not language:
            # Detect primary language
            language = self._detect_primary_language(repo_path)
        
        issues_count = 0
        
        if language == 'python':
            issues_count += self._lint_python(repo_path, linting_results)
        elif language in ['javascript', 'typescript']:
            issues_count += self._lint_javascript(repo_path, linting_results)
        
        # Calculate score
        linting_results["score"] = max(0, 100 - issues_count * 2)
        
        return linting_results
    
    def _detect_primary_language(self, repo_path: Path) -> str:
        """Detect the primary programming language of the repository"""
        language_counts = {}
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                language = self.detect_language(file_path)
                if language != 'unknown':
                    language_counts[language] = language_counts.get(language, 0) + 1
        
        return max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else 'unknown'
    
    def _lint_python(self, repo_path: Path, results: Dict[str, Any]) -> int:
        """Run Python linting tools"""
        issues_count = 0
        
        # Flake8
        try:
            flake8_result = subprocess.run(
                ["flake8", str(repo_path), "--count"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if flake8_result.returncode != 0:
                results["tools_used"].append("flake8")
                issues = flake8_result.stdout.strip().split('\n') if flake8_result.stdout else []
                for issue in issues:
                    if issue.strip():
                        parts = issue.split(':')
                        if len(parts) >= 4:
                            results["issues"].append({
                                "tool": "flake8",
                                "file": parts[0],
                                "line": parts[1],
                                "code": parts[3].split()[0] if len(parts[3].split()) > 0 else "E",
                                "message": parts[3] if len(parts) >= 3 else issue,
                                "severity": "warning"
                            })
                            issues_count += 1
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Black check for formatting
        try:
            black_result = subprocess.run(
                ["black", "--check", "--diff", str(repo_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if black_result.returncode != 0 and black_result.stdout:
                results["tools_used"].append("black")
                results["issues"].append({
                    "tool": "black",
                    "file": "multiple",
                    "message": "Code formatting issues detected",
                    "severity": "info"
                })
                issues_count += 1
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return issues_count
    
    def _lint_javascript(self, repo_path: Path, results: Dict[str, Any]) -> int:
        """Run JavaScript/TypeScript linting tools"""
        issues_count = 0
        
        # ESLint
        try:
            eslint_result = subprocess.run(
                ["eslint", str(repo_path), "--format", "json"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if eslint_result.stdout:
                eslint_data = json.loads(eslint_result.stdout)
                for file_result in eslint_data:
                    results["tools_used"].append("eslint")
                    for message in file_result.get("messages", []):
                        results["issues"].append({
                            "tool": "eslint",
                            "file": file_result.get("filePath", "unknown"),
                            "line": message.get("line", 0),
                            "code": message.get("ruleId", ""),
                            "message": message.get("message", ""),
                            "severity": message.get("severity", "warning") == 2 and "error" or "warning"
                        })
                        issues_count += 1
        
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        
        return issues_count
    
    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Perform comprehensive code quality analysis"""
        repo_path = Path(repo_path)
        
        console.print(f"[blue]Analyzing code quality for {repo_path.name}...[/]")
        
        analysis_results = {
            "repository": str(repo_path),
            "analysis_date": datetime.now().isoformat(),
            "language": self._detect_primary_language(repo_path),
            "overall_score": 0,
            "metrics": {}
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing...", total=100)
            
            # Dependency analysis
            progress.update(task, description="Checking dependencies...", completed=20)
            analysis_results["dependencies"] = self.check_dependencies(repo_path)
            
            # Secret scanning
            progress.update(task, description="Scanning for secrets...", completed=40)
            analysis_results["security"] = self.check_secrets(repo_path)
            
            # Linting analysis
            progress.update(task, description="Running linting tools...", completed=70)
            analysis_results["linting"] = self.run_linting(repo_path, analysis_results["language"])
            
            # File complexity analysis
            progress.update(task, description="Analyzing complexity...", completed=90)
            analysis_results["complexity"] = self._analyze_repo_complexity(repo_path)
            
            progress.update(task, completed=100)
        
        # Calculate overall score
        scores = [
            analysis_results["dependencies"].get("security_score", 100),
            analysis_results["linting"].get("score", 100),
            100 - len(analysis_results["security"].get("secrets", [])) * 10
        ]
        
        analysis_results["overall_score"] = max(0, sum(scores) // len(scores))
        
        return analysis_results
    
    def _analyze_repo_complexity(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze overall repository complexity"""
        complexity_data = {
            "total_files": 0,
            "high_complexity_files": [],
            "average_complexity": 0
        }
        
        total_complexity = 0
        analyzed_files = 0
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and self.detect_language(file_path) in ['python', 'javascript', 'typescript']:
                complexity_result = self.analyze_file_complexity(file_path)
                
                if complexity_result["complexity_score"] < 70:  # High complexity threshold
                    complexity_data["high_complexity_files"].append({
                        "file": str(file_path.relative_to(repo_path)),
                        "score": complexity_result["complexity_score"],
                        "issues": complexity_result["issues"]
                    })
                
                total_complexity += complexity_result["complexity_score"]
                analyzed_files += 1
        
        complexity_data["total_files"] = analyzed_files
        if analyzed_files > 0:
            complexity_data["average_complexity"] = total_complexity / analyzed_files
        
        return complexity_data
    
    def display_quality_report(self, analysis_results: Dict[str, Any]):
        """Display comprehensive code quality report"""
        repo_name = Path(analysis_results["repository"]).name
        
        # Overall Score
        overall_score = analysis_results.get("overall_score", 0)
        score_color = "green" if overall_score >= 80 else "yellow" if overall_score >= 60 else "red"
        
        console.print(Panel(
            f"[bold]Overall Quality Score: [{score_color}]{overall_score}/100[/{score_color}][/bold]\n"
            f"Repository: {repo_name}\n"
            f"Language: {analysis_results.get('language', 'unknown').title()}\n"
            f"Analysis Date: {analysis_results.get('analysis_date', 'unknown')[:19]}",
            title="Code Quality Report",
            border_style=score_color
        ))
        
        # Security Issues
        security_data = analysis_results.get("security", {})
        secrets_found = len(security_data.get("secrets", []))
        
        if secrets_found > 0:
            console.print(Panel(
                f"🚨 [red]Found {secrets_found} potential secrets![/red]",
                title="Security Issues",
                border_style="red"
            ))
        
        # Dependency Security
        deps_data = analysis_results.get("dependencies", {})
        security_score = deps_data.get("security_score", 100)
        vulnerabilities = len(deps_data.get("vulnerabilities", []))
        
        if vulnerabilities > 0:
            console.print(Panel(
                f"⚠️ [yellow]{vulnerabilities} dependency vulnerabilities found[/yellow]\n"
                f"Security Score: {security_score}/100",
                title="Dependency Security",
                border_style="yellow"
            ))
        
        # Linting Results
        linting_data = analysis_results.get("linting", {})
        linting_score = linting_data.get("score", 100)
        issues = linting_data.get("issues", [])
        
        if issues:
            table = Table(title="Linting Issues", box=box.ROUNDED)
            table.add_column("Tool", style="cyan")
            table.add_column("File", style="green")
            table.add_column("Line", justify="right")
            table.add_column("Issue", style="dim")
            
            for issue in issues[:10]:  # Show first 10 issues
                table.add_row(
                    issue.get("tool", ""),
                    Path(issue.get("file", "")).name,
                    str(issue.get("line", "")),
                    issue.get("message", "")[:50] + "..." if len(issue.get("message", "")) > 50 else issue.get("message", "")
                )
            
            console.print(table)
            
            if len(issues) > 10:
                console.print(f"[dim]... and {len(issues) - 10} more issues[/dim]")
        
        # Complexity Analysis
        complexity_data = analysis_results.get("complexity", {})
        high_complexity_files = complexity_data.get("high_complexity_files", [])
        
        if high_complexity_files:
            console.print(Panel(
                f"Found {len(high_complexity_files)} files with high complexity\n"
                f"Average complexity score: {complexity_data.get('average_complexity', 0):.1f}/100",
                title="Complexity Analysis",
                border_style="yellow"
            ))
