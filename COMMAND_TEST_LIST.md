# GitFlow Studio - Command Test List

## 🚀 Quick Test Commands

Run these commands to test all GitFlow Studio functionality:

### Basic Commands
```bash
# Help and version
gitflow-studio --help
gitflow-studio --version

# Repository discovery
gitflow-studio --discover

# Basic status
gitflow-studio --repo . status
gitflow-studio --repo . --verbose status
```

### Git Operations
```bash
# Status and log
gitflow-studio --repo . status
gitflow-studio --repo . log --max-count 5
gitflow-studio --repo . log --graph --oneline --max-count 3
gitflow-studio --repo . log --oneline
gitflow-studio --repo . log --author

# Branches
gitflow-studio --repo . branches

# Commit help (won't actually commit)
gitflow-studio --repo . commit --help
```

### Branch Operations
```bash
# Branch management help
gitflow-studio --repo . branch create --help
gitflow-studio --repo . branch delete --help
gitflow-studio --repo . branch rename --help
```

### Stash Operations
```bash
# Stash commands
gitflow-studio --repo . stash list
gitflow-studio --repo . stash --help
```

### Tag Operations
```bash
# Tag management
gitflow-studio --repo . tag list
gitflow-studio --repo . tag create --help
gitflow-studio --repo . tag delete --help
gitflow-studio --repo . tag show --help
```

### Git Flow Operations
```bash
# Git Flow help
gitflow-studio --repo . gitflow init --help
gitflow-studio --repo . gitflow feature --help
gitflow-studio --repo . gitflow release --help
```

### GitHub Operations
```bash
# GitHub integration
gitflow-studio --repo . github --help
gitflow-studio --repo . github login --help
gitflow-studio --repo . github repos --help
gitflow-studio --repo . github search --help
```

### Analytics Operations
```bash
# Repository analytics
gitflow-studio --repo . analytics --help
gitflow-studio --repo . analytics stats
gitflow-studio --repo . analytics activity 7
gitflow-studio --repo . analytics files
gitflow-studio --repo . analytics branches
gitflow-studio --repo . analytics contributors
gitflow-studio --repo . analytics health
```

### Advanced Git Operations
```bash
# Advanced operations
gitflow-studio --repo . cherry-pick --help
gitflow-studio --repo . revert --help
gitflow-studio --repo . rebase-interactive --help
gitflow-studio --repo . squash --help
```

### Repository Management
```bash
# Repository info
gitflow-studio --repo . repo info
```

### Interactive Mode
```bash
# Interactive mode
gitflow-studio --interactive --help
```

### Error Handling (Expected to fail)
```bash
# These should fail gracefully
gitflow-studio --repo . invalid-command
gitflow-studio --repo /invalid/path status
gitflow-studio --repo . commit
```

## 🧪 Automated Testing

### Run Complete Test Suite
```bash
# Run the comprehensive test script
python3 test_all_commands.py

# Or run directly
./test_all_commands.py
```

### Test Categories Covered
1. **Basic Commands** - Help, version, discovery
2. **Git Operations** - Status, log, branches
3. **Branch Operations** - Create, delete, rename
4. **Stash Operations** - List, create, pop
5. **Tag Operations** - List, create, delete, show
6. **Git Flow Operations** - Init, feature, release
7. **GitHub Operations** - Login, repos, search
8. **Analytics Operations** - Stats, activity, files, branches, contributors, health
9. **Advanced Git Operations** - Cherry-pick, revert, rebase, squash
10. **Log Variations** - Different log options
11. **Repository Management** - Info, discovery
12. **Error Handling** - Invalid commands and paths
13. **Interactive Mode** - Basic interactive functionality

## 📊 Expected Results

### All Commands Should:
- ✅ Return appropriate exit codes (0 for success, 1-2 for errors)
- ✅ Display help text when `--help` is used
- ✅ Handle errors gracefully
- ✅ Show meaningful output or error messages

### Success Criteria:
- **Help Commands**: Should display help text
- **Status Commands**: Should show repository status
- **List Commands**: Should show lists (branches, tags, stashes)
- **Analytics Commands**: Should display statistics and data
- **Error Commands**: Should fail with appropriate error messages

## 🎯 Quick Test Script

```bash
#!/bin/bash
# Quick test script - run this to test basic functionality

echo "🧪 Testing GitFlow Studio Commands..."

# Test basic commands
echo "Testing basic commands..."
gitflow-studio --help > /dev/null && echo "✅ Help command works" || echo "❌ Help command failed"
gitflow-studio --discover > /dev/null && echo "✅ Discover command works" || echo "❌ Discover command failed"

# Test git operations
echo "Testing git operations..."
gitflow-studio --repo . status > /dev/null && echo "✅ Status command works" || echo "❌ Status command failed"
gitflow-studio --repo . log --max-count 3 > /dev/null && echo "✅ Log command works" || echo "❌ Log command failed"

# Test analytics
echo "Testing analytics..."
gitflow-studio --repo . analytics stats > /dev/null && echo "✅ Analytics stats works" || echo "❌ Analytics stats failed"

echo "🎉 Basic testing complete!"
```

## 📝 Testing Notes

### Before PyPI Upload:
1. **Run automated tests**: `python3 test_all_commands.py`
2. **Check all help commands**: Ensure help text displays correctly
3. **Test error handling**: Verify invalid commands fail gracefully
4. **Verify analytics**: Check that all analytics commands work
5. **Test interactive mode**: Ensure interactive mode starts correctly

### Common Issues to Watch For:
- **Missing dependencies**: Ensure all required packages are installed
- **Git repository**: Make sure you're in a Git repository for Git operations
- **Permissions**: Some operations might require specific permissions
- **Network**: GitHub operations require internet connection

### Success Indicators:
- All help commands display properly
- Git operations work in a Git repository
- Analytics commands show data or appropriate messages
- Error handling works for invalid inputs
- Interactive mode starts without errors

---

**Run the automated test suite for comprehensive testing before PyPI upload! 🚀** 