# GitFlow Studio - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install GitFlow Studio

**Linux/macOS:**
```bash
git clone https://github.com/Sherin-SEF-AI/GitFlow-Studio.git
cd GitFlow-Studio
./install.sh
```

**Windows:**
```cmd
git clone https://github.com/Sherin-SEF-AI/GitFlow-Studio.git
cd GitFlow-Studio
install.bat
```

### Step 2: Activate Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate.bat
```

### Step 3: Try GitFlow Studio

```bash
# See the beautiful interface
gitflow-studio --help

# Discover Git repositories
gitflow-studio --discover

# Start interactive mode
gitflow-studio --interactive
```

## 🎯 First Commands

### Discover Your Repositories
```bash
gitflow-studio --discover
```
This will find all Git repositories in your current directory and show them in a beautiful table.

### Check Repository Status
```bash
gitflow-studio --repo /path/to/your/repo status
```
Get a detailed status with file counts and visual indicators.

### View Commit History
```bash
gitflow-studio --repo /path/to/your/repo log --max-count 10
```
See your commit history with beautiful formatting.

### List Branches
```bash
gitflow-studio --repo /path/to/your/repo branch list
```
View all branches with current branch highlighted.

## 🎮 Interactive Mode

Start interactive mode for a guided experience:
```bash
gitflow-studio --interactive
```

In interactive mode, you can:
- Type `help` for available commands
- Use `discover` to find repositories
- Run Git commands without typing the full path
- Get real-time feedback and progress indicators

## 🔧 Common Workflows

### Daily Development
```bash
# Check status
gitflow-studio --repo /path/to/repo status

# Create a feature branch
gitflow-studio --repo /path/to/repo branch create feature/new-feature

# Switch to the branch
gitflow-studio --repo /path/to/repo branch checkout feature/new-feature

# Make changes, then commit
gitflow-studio --repo /path/to/repo commit "Add new feature" --add-all

# Push changes
gitflow-studio --repo /path/to/repo push
```

### Git Flow Workflow
```bash
# Initialize Git Flow
gitflow-studio --repo /path/to/repo gitflow init

# Start a feature
gitflow-studio --repo /path/to/repo gitflow feature-start my-feature

# Finish a feature
gitflow-studio --repo /path/to/repo gitflow feature-finish my-feature

# Start a release
gitflow-studio --repo /path/to/repo gitflow release-start v1.0.0

# Finish a release
gitflow-studio --repo /path/to/repo gitflow release-finish v1.0.0
```

### Stash Management
```bash
# Create a stash
gitflow-studio --repo /path/to/repo stash create --message "WIP: feature in progress"

# List stashes
gitflow-studio --repo /path/to/repo stash list

# Apply a stash
gitflow-studio --repo /path/to/repo stash pop
```

## 🎨 What Makes GitFlow Studio Special

### Beautiful Interface
- **ASCII art banner** with colorful branding
- **Progress indicators** for all operations
- **Structured tables** and panels
- **Color-coded information** for easy reading

### Enhanced Features
- **Repository discovery** - Find Git repos automatically
- **Interactive mode** - Guided command-line experience
- **Real-time progress** - See operations happening live
- **Comprehensive help** - Built-in documentation

### Professional Quality
- **Async operations** - Non-blocking Git commands
- **Error handling** - Clear, helpful error messages
- **Plugin system** - Extensible architecture
- **Cross-platform** - Works on Linux, macOS, and Windows

## 🆘 Need Help?

### Built-in Help
```bash
# General help
gitflow-studio --help

# Command-specific help
gitflow-studio --repo /path/to/repo branch --help
gitflow-studio --repo /path/to/repo gitflow --help
```

### Interactive Help
```bash
gitflow-studio --interactive
# Then type: help
```

### Documentation
- **README.md** - Basic usage and examples
- **INSTALLATION.md** - Detailed installation guide
- **FEATURE_SUMMARY.md** - Complete feature overview

## 🎉 You're Ready!

GitFlow Studio is now installed and ready to use. Start with:

1. **Discover repositories**: `gitflow-studio --discover`
2. **Try interactive mode**: `gitflow-studio --interactive`
3. **Check a repository**: `gitflow-studio --repo /path/to/repo status`

Enjoy your beautiful Git workflow management experience! 🚀 