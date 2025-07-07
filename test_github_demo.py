#!/usr/bin/env python3
"""
Demo script to show GitHub integration working
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the studio directory to the path
sys.path.insert(0, str(Path(__file__).parent / "studio"))

from studio.github.auth import GitHubAuth
from studio.github.repos import GitHubRepos

async def demo_github_integration():
    """Demo the GitHub integration"""
    print("🚀 GitFlow Studio - GitHub Integration Demo")
    print("=" * 60)
    
    # Initialize GitHub components
    auth = GitHubAuth()
    repos = GitHubRepos(auth)
    
    print(f"✅ Client ID: {auth.client_id}")
    print(f"✅ Client Secret: {'*' * len(auth.client_secret) if auth.client_secret != 'your_github_oauth_app_client_secret' else 'Not set'}")
    
    # Check if authenticated
    if auth.is_authenticated():
        print("✅ Already authenticated!")
        user_info = auth.get_user_info()
        if user_info:
            print(f"👤 User: {user_info.get('login', 'Unknown')}")
            print(f"📧 Name: {user_info.get('name', 'Unknown')}")
    else:
        print("ℹ️  Not authenticated yet")
        print("   Run: python -m studio --github-login")
        return
    
    # List repositories
    print("\n📚 Fetching your repositories...")
    try:
        user_repos = await repos.list_repositories()
        print(f"✅ Found {len(user_repos)} repositories!")
        
        if user_repos:
            print("\n📋 Your repositories:")
            for i, repo in enumerate(user_repos[:5], 1):  # Show first 5
                print(f"  {i}. {repo['name']} ({repo.get('language', 'N/A')}) - {repo.get('description', 'No description')[:50]}...")
            
            if len(user_repos) > 5:
                print(f"  ... and {len(user_repos) - 5} more repositories")
        
    except Exception as e:
        print(f"❌ Error fetching repositories: {e}")
    
    # Search repositories
    print("\n🔍 Searching for 'git workflow' repositories...")
    try:
        search_results = await repos.search_repositories("git workflow", limit=3)
        print(f"✅ Found {len(search_results)} search results!")
        
        if search_results:
            print("\n🔍 Search results:")
            for i, repo in enumerate(search_results, 1):
                print(f"  {i}. {repo['full_name']} ({repo.get('language', 'N/A')}) - ⭐ {repo.get('stargazers_count', 0)}")
        
    except Exception as e:
        print(f"❌ Error searching repositories: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 GitHub Integration Demo Complete!")
    print("\nNext steps:")
    print("1. Use interactive mode: python -m studio --interactive")
    print("2. Clone a repository: python -m studio github clone <repo-name>")
    print("3. Search repositories: python -m studio github search <query>")

if __name__ == "__main__":
    # Set environment variables if not already set
    if not os.getenv('GITHUB_CLIENT_ID'):
        os.environ['GITHUB_CLIENT_ID'] = "Ov23liSMnnBiFb1fjGiZ"
    if not os.getenv('GITHUB_CLIENT_SECRET'):
        os.environ['GITHUB_CLIENT_SECRET'] = "0d57821a57127932802aa400e967dddc3b7e9ba4"
    
    try:
        asyncio.run(demo_github_integration())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}") 