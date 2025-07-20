#!/usr/bin/env python3
"""
Comprehensive test script for all GitFlow Studio commands
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔍 Testing: {description}")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"   ✅ SUCCESS")
            return True
        else:
            print(f"   ❌ FAILED (exit code: {result.returncode})")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⏰ TIMEOUT")
        return False
    except Exception as e:
        print(f"   💥 EXCEPTION: {e}")
        return False

def test_basic_commands():
    """Test basic GitFlow Studio commands"""
    print("\n🚀 Testing Basic Commands")
    print("=" * 50)
    
    commands = [
        ("python -m studio --help", "Help command"),
        ("python -m studio --repo . status", "Status command"),
        ("python -m studio --repo . log --max-count 2", "Log command"),
        ("python -m studio --repo . branch list", "Branch list command"),
    ]
    
    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc):
            success_count += 1
        print()
    
    return success_count, len(commands)

def test_analytics_commands():
    """Test analytics commands"""
    print("\n📊 Testing Analytics Commands")
    print("=" * 50)
    
    commands = [
        ("python -m studio --repo . analytics stats", "Analytics stats"),
        ("python -m studio --repo . analytics health", "Analytics health"),
        ("python -m studio --repo . analytics contributors", "Analytics contributors"),
        ("python -m studio --repo . analytics activity --days 30", "Analytics activity"),
        ("python -m studio --repo . analytics files --days 30", "Analytics files"),
        ("python -m studio --repo . analytics branches", "Analytics branches"),
    ]
    
    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc):
            success_count += 1
        print()
    
    return success_count, len(commands)

def test_github_commands():
    """Test GitHub commands"""
    print("\n🔗 Testing GitHub Commands")
    print("=" * 50)
    
    commands = [
        ("python -m studio --repo . github repos", "GitHub repos list"),
    ]
    
    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc):
            success_count += 1
        print()
    
    return success_count, len(commands)

def test_gitflow_commands():
    """Test GitFlow commands"""
    print("\n🌊 Testing GitFlow Commands")
    print("=" * 50)
    
    # Note: GitFlow init might fail if there are unstaged changes
    commands = [
        ("python -m studio --repo . gitflow init", "GitFlow init"),
    ]
    
    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc):
            success_count += 1
        print()
    
    return success_count, len(commands)

def test_stash_commands():
    """Test stash commands"""
    print("\n📦 Testing Stash Commands")
    print("=" * 50)
    
    commands = [
        ("python -m studio --repo . stash list --repo .", "Stash list"),
    ]
    
    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc):
            success_count += 1
        print()
    
    return success_count, len(commands)

def test_tag_commands():
    """Test tag commands"""
    print("\n🏷️ Testing Tag Commands")
    print("=" * 50)
    
    commands = [
        ("python -m studio --repo . tag list --repo .", "Tag list"),
    ]
    
    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc):
            success_count += 1
        print()
    
    return success_count, len(commands)

def test_production_features():
    """Test production features"""
    print("\n🚀 Testing Production Features")
    print("=" * 50)
    
    # Test production features test script
    if run_command("python test_production_features.py", "Production features test"):
        print()
        return 1, 1
    else:
        print()
        return 0, 1

def test_interactive_mode():
    """Test interactive mode"""
    print("\n🎯 Testing Interactive Mode")
    print("=" * 50)
    
    # Test interactive mode with basic commands
    test_commands = "discover\nrepo .\nalias list\ntheme list\nexport list\nperformance summary\nquit\n"
    
    cmd = f"echo -e '{test_commands}' | python -m studio --interactive"
    if run_command(cmd, "Interactive mode with production features"):
        print()
        return 1, 1
    else:
        print()
        return 0, 1

def main():
    """Run all command tests"""
    print("🧪 GitFlow Studio - Comprehensive Command Test")
    print("=" * 60)
    
    total_success = 0
    total_commands = 0
    
    # Test all command categories
    test_functions = [
        test_basic_commands,
        test_analytics_commands,
        test_github_commands,
        test_gitflow_commands,
        test_stash_commands,
        test_tag_commands,
        test_production_features,
        test_interactive_mode,
    ]
    
    for test_func in test_functions:
        success, total = test_func()
        total_success += success
        total_commands += total
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successful Commands: {total_success}")
    print(f"❌ Failed Commands: {total_commands - total_success}")
    print(f"📊 Total Commands: {total_commands}")
    print(f"🎯 Success Rate: {(total_success/total_commands*100):.1f}%")
    
    if total_success == total_commands:
        print("\n🎉 ALL COMMANDS WORKING PERFECTLY!")
        print("🚀 GitFlow Studio is ready for production use!")
        return 0
    else:
        print(f"\n⚠️ {total_commands - total_success} commands need attention")
        print("🔧 Please check the failed commands above")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 