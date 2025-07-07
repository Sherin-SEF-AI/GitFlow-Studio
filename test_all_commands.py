#!/usr/bin/env python3
"""
GitFlow Studio - Comprehensive Command Test Script
Tests all commands to ensure they work correctly before PyPI upload.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

class GitFlowStudioTester:
    def __init__(self):
        self.test_results = []
        self.current_test = 0
        self.total_tests = 0
        
    def run_command(self, command, description, expected_exit_code=0, timeout=30):
        """Run a command and record the result."""
        self.current_test += 1
        print(f"\n🔍 Test {self.current_test}/{self.total_tests}: {description}")
        print(f"   Command: {command}")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            success = result.returncode == expected_exit_code
            status = "✅ PASS" if success else "❌ FAIL"
            
            print(f"   {status} (Exit code: {result.returncode})")
            
            if result.stdout:
                print(f"   Output: {result.stdout[:200]}...")
            if result.stderr and not success:
                print(f"   Error: {result.stderr[:200]}...")
                
            self.test_results.append({
                'test': self.current_test,
                'description': description,
                'command': command,
                'success': success,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            })
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"   ❌ TIMEOUT (>{timeout}s)")
            self.test_results.append({
                'test': self.current_test,
                'description': description,
                'command': command,
                'success': False,
                'exit_code': -1,
                'stdout': '',
                'stderr': 'Timeout'
            })
            return False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            self.test_results.append({
                'test': self.current_test,
                'description': description,
                'command': command,
                'success': False,
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e)
            })
            return False

    def test_basic_commands(self):
        """Test basic GitFlow Studio commands."""
        print("\n" + "="*60)
        print("🧪 TESTING BASIC COMMANDS")
        print("="*60)
        
        # Test help command
        self.run_command("gitflow-studio --help", "Help command")
        
        # Test version
        self.run_command("gitflow-studio --version", "Version command", expected_exit_code=0)
        
        # Test discover command
        self.run_command("gitflow-studio --discover", "Repository discovery")
        
        # Test with current directory
        self.run_command("gitflow-studio --repo . status", "Status command")
        
        # Test verbose mode
        self.run_command("gitflow-studio --repo . --verbose status", "Verbose status")

    def test_git_operations(self):
        """Test Git operations."""
        print("\n" + "="*60)
        print("🔧 TESTING GIT OPERATIONS")
        print("="*60)
        
        # Test status
        self.run_command("gitflow-studio --repo . status", "Git status")
        
        # Test log
        self.run_command("gitflow-studio --repo . log --max-count 5", "Git log (5 commits)")
        
        # Test log with graph
        self.run_command("gitflow-studio --repo . log --graph --oneline --max-count 3", "Git log with graph")
        
        # Test branches
        self.run_command("gitflow-studio --repo . branches", "List branches")
        
        # Test commit (dry run - won't actually commit)
        self.run_command("gitflow-studio --repo . commit --help", "Commit help")

    def test_branch_operations(self):
        """Test branch operations."""
        print("\n" + "="*60)
        print("🌿 TESTING BRANCH OPERATIONS")
        print("="*60)
        
        # Test branch create help
        self.run_command("gitflow-studio --repo . branch create --help", "Branch create help")
        
        # Test branch delete help
        self.run_command("gitflow-studio --repo . branch delete --help", "Branch delete help")
        
        # Test branch rename help
        self.run_command("gitflow-studio --repo . branch rename --help", "Branch rename help")

    def test_stash_operations(self):
        """Test stash operations."""
        print("\n" + "="*60)
        print("📦 TESTING STASH OPERATIONS")
        print("="*60)
        
        # Test stash list
        self.run_command("gitflow-studio --repo . stash list", "Stash list")
        
        # Test stash help
        self.run_command("gitflow-studio --repo . stash --help", "Stash help")

    def test_tag_operations(self):
        """Test tag operations."""
        print("\n" + "="*60)
        print("🏷️ TESTING TAG OPERATIONS")
        print("="*60)
        
        # Test tag list
        self.run_command("gitflow-studio --repo . tag list", "Tag list")
        
        # Test tag create help
        self.run_command("gitflow-studio --repo . tag create --help", "Tag create help")
        
        # Test tag delete help
        self.run_command("gitflow-studio --repo . tag delete --help", "Tag delete help")
        
        # Test tag show help
        self.run_command("gitflow-studio --repo . tag show --help", "Tag show help")

    def test_gitflow_operations(self):
        """Test Git Flow operations."""
        print("\n" + "="*60)
        print("🌊 TESTING GIT FLOW OPERATIONS")
        print("="*60)
        
        # Test gitflow init help
        self.run_command("gitflow-studio --repo . gitflow init --help", "GitFlow init help")
        
        # Test gitflow feature help
        self.run_command("gitflow-studio --repo . gitflow feature --help", "GitFlow feature help")
        
        # Test gitflow release help
        self.run_command("gitflow-studio --repo . gitflow release --help", "GitFlow release help")

    def test_github_operations(self):
        """Test GitHub operations."""
        print("\n" + "="*60)
        print("🔗 TESTING GITHUB OPERATIONS")
        print("="*60)
        
        # Test github help
        self.run_command("gitflow-studio --repo . github --help", "GitHub help")
        
        # Test github login help
        self.run_command("gitflow-studio --repo . github login --help", "GitHub login help")
        
        # Test github repos help
        self.run_command("gitflow-studio --repo . github repos --help", "GitHub repos help")
        
        # Test github search help
        self.run_command("gitflow-studio --repo . github search --help", "GitHub search help")

    def test_analytics_operations(self):
        """Test analytics operations."""
        print("\n" + "="*60)
        print("📊 TESTING ANALYTICS OPERATIONS")
        print("="*60)
        
        # Test analytics help
        self.run_command("gitflow-studio --repo . analytics --help", "Analytics help")
        
        # Test analytics stats
        self.run_command("gitflow-studio --repo . analytics stats", "Repository statistics")
        
        # Test analytics activity
        self.run_command("gitflow-studio --repo . analytics activity 7", "Commit activity (7 days)")
        
        # Test analytics files
        self.run_command("gitflow-studio --repo . analytics files", "File statistics")
        
        # Test analytics branches
        self.run_command("gitflow-studio --repo . analytics branches", "Branch analytics")
        
        # Test analytics contributors
        self.run_command("gitflow-studio --repo . analytics contributors", "Contributor statistics")
        
        # Test analytics health
        self.run_command("gitflow-studio --repo . analytics health", "Repository health")

    def test_advanced_git_operations(self):
        """Test advanced Git operations."""
        print("\n" + "="*60)
        print("🔄 TESTING ADVANCED GIT OPERATIONS")
        print("="*60)
        
        # Test cherry-pick help
        self.run_command("gitflow-studio --repo . cherry-pick --help", "Cherry-pick help")
        
        # Test revert help
        self.run_command("gitflow-studio --repo . revert --help", "Revert help")
        
        # Test rebase-interactive help
        self.run_command("gitflow-studio --repo . rebase-interactive --help", "Interactive rebase help")
        
        # Test squash help
        self.run_command("gitflow-studio --repo . squash --help", "Squash help")

    def test_log_variations(self):
        """Test different log command variations."""
        print("\n" + "="*60)
        print("📋 TESTING LOG VARIATIONS")
        print("="*60)
        
        # Test log with different options
        self.run_command("gitflow-studio --repo . log --max-count 3", "Log with max count")
        self.run_command("gitflow-studio --repo . log --oneline", "Log oneline")
        self.run_command("gitflow-studio --repo . log --graph", "Log with graph")
        self.run_command("gitflow-studio --repo . log --author", "Log with author filter")

    def test_repository_management(self):
        """Test repository management commands."""
        print("\n" + "="*60)
        print("📁 TESTING REPOSITORY MANAGEMENT")
        print("="*60)
        
        # Test repo info
        self.run_command("gitflow-studio --repo . repo info", "Repository information")

    def test_error_handling(self):
        """Test error handling with invalid commands."""
        print("\n" + "="*60)
        print("⚠️ TESTING ERROR HANDLING")
        print("="*60)
        
        # Test invalid command
        self.run_command("gitflow-studio --repo . invalid-command", "Invalid command", expected_exit_code=2)
        
        # Test invalid repository path
        self.run_command("gitflow-studio --repo /invalid/path status", "Invalid repository path", expected_exit_code=1)
        
        # Test missing required arguments
        self.run_command("gitflow-studio --repo . commit", "Missing commit message", expected_exit_code=2)

    def test_interactive_mode(self):
        """Test interactive mode (basic check)."""
        print("\n" + "="*60)
        print("🎯 TESTING INTERACTIVE MODE")
        print("="*60)
        
        # Test interactive mode help
        self.run_command("gitflow-studio --interactive --help", "Interactive mode help")

    def run_all_tests(self):
        """Run all test categories."""
        print("🚀 GitFlow Studio - Comprehensive Command Test Suite")
        print("="*60)
        print(f"Testing GitFlow Studio version: {self.get_version()}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python version: {sys.version}")
        print("="*60)
        
        # Count total tests
        test_methods = [
            self.test_basic_commands,
            self.test_git_operations,
            self.test_branch_operations,
            self.test_stash_operations,
            self.test_tag_operations,
            self.test_gitflow_operations,
            self.test_github_operations,
            self.test_analytics_operations,
            self.test_advanced_git_operations,
            self.test_log_variations,
            self.test_repository_management,
            self.test_error_handling,
            self.test_interactive_mode
        ]
        
        # Estimate total tests (approximate)
        self.total_tests = len(test_methods) * 5  # Average 5 tests per category
        
        # Run all test categories
        for test_method in test_methods:
            try:
                test_method()
                time.sleep(1)  # Brief pause between categories
            except Exception as e:
                print(f"❌ Error in {test_method.__name__}: {e}")
        
        self.print_summary()

    def get_version(self):
        """Get GitFlow Studio version."""
        try:
            result = subprocess.run(
                "gitflow-studio --version", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except:
            return "Unknown"

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - Test {result['test']}: {result['description']}")
                    print(f"    Command: {result['command']}")
                    print(f"    Exit Code: {result['exit_code']}")
                    if result['stderr']:
                        print(f"    Error: {result['stderr'][:100]}...")
                    print()
        
        # Save detailed results to file
        self.save_results()
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! GitFlow Studio is ready for PyPI upload!")
        else:
            print("⚠️ Some tests failed. Please review before PyPI upload.")

    def save_results(self):
        """Save detailed test results to file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("GitFlow Studio - Command Test Results\n")
            f.write("="*50 + "\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Version: {self.get_version()}\n\n")
            
            for result in self.test_results:
                f.write(f"Test {result['test']}: {result['description']}\n")
                f.write(f"Command: {result['command']}\n")
                f.write(f"Status: {'PASS' if result['success'] else 'FAIL'}\n")
                f.write(f"Exit Code: {result['exit_code']}\n")
                if result['stdout']:
                    f.write(f"Output: {result['stdout'][:500]}...\n")
                if result['stderr']:
                    f.write(f"Error: {result['stderr'][:500]}...\n")
                f.write("-"*50 + "\n")
        
        print(f"📄 Detailed results saved to: {filename}")

def main():
    """Main function to run the test suite."""
    tester = GitFlowStudioTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        tester.print_summary()
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {e}")
        tester.print_summary()

if __name__ == "__main__":
    main() 