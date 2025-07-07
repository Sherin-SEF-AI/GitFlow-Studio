"""
GitHub integration module for GitFlow Studio
Provides authentication and repository access via GitHub API
"""

from .auth import GitHubAuth
from .repos import GitHubRepos

__all__ = ['GitHubAuth', 'GitHubRepos'] 