#!/usr/bin/env python3
"""
Test script for GitHub integration functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the studio directory to the path
sys.path.insert(0, str(Path(__file__).parent / "studio"))

from studio.github.auth import GitHubAuth
from studio.github.repos import GitHubRepos

async def test_github_integration():
    """Test GitHub integration functionality"""
    print("🧪 Testing GitHub Integration")
    print("=" * 50)
    
    # Test 1: Initialize GitHub Auth
    print("\n1. Testing GitHub Auth initialization...")
    try:
        auth = GitHubAuth()
        print("✅ GitHub Auth initialized successfully")
        
        # Check if credentials are configured
        if (auth.client_id == "your_github_oauth_app_client_id" or 
            auth.client_secret == "your_github_oauth_app_client_secret"):
            print("⚠️  GitHub OAuth credentials not configured")
            print("   Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables")
            print("   See GITHUB_INTEGRATION.md for setup instructions")
        else:
            print("✅ GitHub OAuth credentials are configured")
            
    except Exception as e:
        print(f"❌ Failed to initialize GitHub Auth: {e}")
        return False
    
    # Test 2: Initialize GitHub Repos
    print("\n2. Testing GitHub Repos initialization...")
    try:
        repos = GitHubRepos(auth)
        print("✅ GitHub Repos initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize GitHub Repos: {e}")
        return False
    
    # Test 3: Check authentication status
    print("\n3. Testing authentication status...")
    try:
        is_authenticated = auth.is_authenticated()
        if is_authenticated:
            print("✅ User is authenticated")
            user_info = auth.get_user_info()
            if user_info:
                print(f"   User: {user_info.get('login', 'Unknown')}")
                print(f"   Name: {user_info.get('name', 'Unknown')}")
        else:
            print("ℹ️  User is not authenticated")
            print("   Use 'github login' command to authenticate")
    except Exception as e:
        print(f"❌ Failed to check authentication status: {e}")
        return False
    
    # Test 4: Test configuration directory
    print("\n4. Testing configuration directory...")
    try:
        config_dir = auth.config_dir
        if config_dir.exists():
            print(f"✅ Configuration directory exists: {config_dir}")
        else:
            print(f"ℹ️  Configuration directory will be created: {config_dir}")
    except Exception as e:
        print(f"❌ Failed to check configuration directory: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 GitHub Integration Test Completed!")
    print("\nNext steps:")
    print("1. Set up GitHub OAuth credentials (see GITHUB_INTEGRATION.md)")
    print("2. Run: python -m studio --github-login")
    print("3. Test repository operations")
    
    return True

def test_dependencies():
    """Test if required dependencies are available"""
    print("🔍 Checking Dependencies")
    print("=" * 30)
    
    dependencies = [
        ('aiohttp', 'aiohttp'),
        ('cryptography', 'cryptography'),
        ('keyring', 'keyring'),
        ('rich', 'rich')
    ]
    
    missing_deps = []
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - Missing")
            missing_deps.append(package_name)
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies are available")
        return True

if __name__ == "__main__":
    print("🚀 GitFlow Studio - GitHub Integration Test")
    print("=" * 60)
    
    # Test dependencies first
    if not test_dependencies():
        sys.exit(1)
    
    # Test GitHub integration
    try:
        success = asyncio.run(test_github_integration())
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1) 