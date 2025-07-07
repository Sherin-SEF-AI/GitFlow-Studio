#!/bin/bash

# GitFlow Studio - Quick Test Script
# Tests the most important commands quickly

echo "🧪 GitFlow Studio - Quick Test Script"
echo "====================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
total_tests=0
passed_tests=0

# Function to run a test
run_test() {
    local description="$1"
    local command="$2"
    local expected_exit="$3"
    
    total_tests=$((total_tests + 1))
    echo -n "Test $total_tests: $description... "
    
    # Run command and capture exit code
    eval "$command" > /dev/null 2>&1
    exit_code=$?
    
    if [ $exit_code -eq ${expected_exit:-0} ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        passed_tests=$((passed_tests + 1))
    else
        echo -e "${RED}❌ FAIL (exit code: $exit_code)${NC}"
    fi
}

echo "🔍 Testing Basic Commands..."
run_test "Help command" "gitflow-studio --help"
run_test "Repository discovery" "gitflow-studio --discover"
run_test "Status command" "gitflow-studio --repo . status"
run_test "Verbose status" "gitflow-studio --repo . --verbose status"

echo ""
echo "🔧 Testing Git Operations..."
run_test "Git log (5 commits)" "gitflow-studio --repo . log --max-count 5"
run_test "Git log help" "gitflow-studio --repo . log --help"
run_test "List branches" "gitflow-studio --repo . branch list"
run_test "Commit help" "gitflow-studio --repo . commit --help"

echo ""
echo "🌿 Testing Branch Operations..."
run_test "Branch help" "gitflow-studio --repo . branch --help"
run_test "Branch create help" "gitflow-studio --repo . branch create --help"
run_test "Branch delete help" "gitflow-studio --repo . branch delete --help"
run_test "Branch rename help" "gitflow-studio --repo . branch rename --help"
run_test "Branch checkout help" "gitflow-studio --repo . branch checkout --help"

echo ""
echo "📦 Testing Stash Operations..."
run_test "Stash list" "gitflow-studio --repo . stash list"
run_test "Stash help" "gitflow-studio --repo . stash --help"

echo ""
echo "🏷️ Testing Tag Operations..."
run_test "Tag list" "gitflow-studio --repo . tag list"
run_test "Tag create help" "gitflow-studio --repo . tag create --help"
run_test "Tag delete help" "gitflow-studio --repo . tag delete --help"
run_test "Tag show help" "gitflow-studio --repo . tag show --help"

echo ""
echo "🌊 Testing Git Flow Operations..."
run_test "GitFlow help" "gitflow-studio --repo . gitflow --help"
run_test "GitFlow init help" "gitflow-studio --repo . gitflow init --help"
run_test "GitFlow feature help" "gitflow-studio --repo . gitflow feature --help"
run_test "GitFlow release help" "gitflow-studio --repo . gitflow release --help"

echo ""
echo "🔗 Testing GitHub Operations..."
run_test "GitHub help" "gitflow-studio --repo . github --help"
run_test "GitHub login help" "gitflow-studio --repo . github login --help"
run_test "GitHub repos help" "gitflow-studio --repo . github repos --help"
run_test "GitHub search help" "gitflow-studio --repo . github search --help"

echo ""
echo "📊 Testing Analytics Operations..."
run_test "Analytics help" "gitflow-studio --repo . analytics --help"
run_test "Repository statistics" "gitflow-studio --repo . analytics stats"
run_test "Commit activity" "gitflow-studio --repo . analytics activity 7"
run_test "File statistics" "gitflow-studio --repo . analytics files"
run_test "Branch analytics" "gitflow-studio --repo . analytics branches"
run_test "Contributor statistics" "gitflow-studio --repo . analytics contributors"
run_test "Repository health" "gitflow-studio --repo . analytics health"

echo ""
echo "🔄 Testing Advanced Git Operations..."
run_test "Cherry-pick help" "gitflow-studio --repo . cherry-pick --help"
run_test "Revert help" "gitflow-studio --repo . revert --help"
run_test "Interactive rebase help" "gitflow-studio --repo . rebase-interactive --help"
run_test "Squash help" "gitflow-studio --repo . squash --help"

echo ""
echo "📋 Testing Additional Commands..."
run_test "Log file help" "gitflow-studio --repo . log-file --help"
run_test "Show commit help" "gitflow-studio --repo . show-commit --help"
run_test "Push help" "gitflow-studio --repo . push --help"
run_test "Pull help" "gitflow-studio --repo . pull --help"

echo ""
echo "📁 Testing Repository Management..."
run_test "Repository info" "gitflow-studio --repo . repo info"

echo ""
echo "🎯 Testing Interactive Mode..."
run_test "Interactive mode help" "gitflow-studio --interactive --help"

echo ""
echo "⚠️ Testing Error Handling..."
run_test "Invalid command (should fail)" "gitflow-studio --repo . invalid-command" 2
run_test "Invalid repo path (should fail)" "gitflow-studio --repo /invalid/path status" 1
run_test "Missing commit message (should fail)" "gitflow-studio --repo . commit" 2

echo ""
echo "====================================="
echo "📊 TEST SUMMARY"
echo "====================================="
echo "Total Tests: $total_tests"
echo -e "✅ Passed: ${GREEN}$passed_tests${NC}"
echo -e "❌ Failed: ${RED}$((total_tests - passed_tests))${NC}"

if [ $passed_tests -eq $total_tests ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL TESTS PASSED! GitFlow Studio is ready for PyPI upload!${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️ Some tests failed. Please review before PyPI upload.${NC}"
    exit 1
fi 