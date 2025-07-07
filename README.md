# GitFlow Studio 🚀

A comprehensive CLI tool for Git and GitHub workflow management with advanced analytics, interactive mode, and powerful Git operations.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/badge/PyPI-gitflow--studio-blue.svg)](https://pypi.org/project/gitflow-studio/)

## ✨ Features

- 🔧 **Git Operations**: Status, commit, push, pull, branch management
- 🌊 **Git Flow**: Feature, release, and hotfix branch workflows
- 🔗 **GitHub Integration**: Repository listing, cloning, search, OAuth authentication
- 📊 **Analytics**: Repository statistics, commit activity, contributor insights
- 🎯 **Interactive Mode**: User-friendly command-line interface
- 🔄 **Advanced Git**: Cherry-pick, revert, interactive rebase, squash
- 🏷️ **Tag Management**: Create, delete, list, and show tags
- 📦 **Stash Operations**: Create, list, and pop stashes
- 🔍 **Repository Discovery**: Find Git repositories automatically
- 🎨 **Rich UI**: Beautiful tables, panels, and formatted output

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install gitflow-studio

# Or use the installation script
curl -sSL https://raw.githubusercontent.com/Sherin-SEF-AI/GitFlow-Studio/main/install.sh | bash
```

### Basic Usage

```bash
# Show help
gitflow-studio --help

# Interactive mode
gitflow-studio --interactive

# Discover repositories
gitflow-studio --discover

# Show repository status
gitflow-studio --repo /path/to/repo status
```

## 📋 Commands Overview

### Repository Management
- `discover` - Find Git repositories in current directory
- `repo info` - Show current repository information

### Git Operations
- `status` - Show repository status
- `log` - Show commit log
- `branches` - List all branches
- `checkout <ref>` - Checkout branch or commit
- `commit <message>` - Create commit with message
- `push` - Push changes to remote
- `pull` - Pull changes from remote

### Branch Management
- `branch create <name>` - Create new branch
- `branch delete <name>` - Delete local branch
- `branch delete-remote <name>` - Delete remote branch
- `branch rename <old> <new>` - Rename branch

### Advanced Git Operations
- `cherry-pick <hash>` - Cherry-pick a commit
- `revert <hash>` - Revert a commit
- `rebase-interactive <base>` - Interactive rebase
- `squash <count>` - Squash last N commits

### Stash Operations
- `stash [message]` - Create stash (optional message)
- `stash list` - List all stashes
- `stash pop` - Pop latest stash

### Tag Operations
- `tag list` - List all tags
- `tag create <name>` - Create a new tag
- `tag delete <name>` - Delete a tag
- `tag show <name>` - Show tag details

### Git Flow Operations
- `gitflow init` - Initialize Git Flow
- `gitflow feature start <name>` - Start feature branch
- `gitflow feature finish <name>` - Finish feature branch
- `gitflow release start <version>` - Start release branch
- `gitflow release finish <version>` - Finish release branch

### GitHub Operations
- `github login` - Login to GitHub
- `github logout` - Logout from GitHub
- `github repos` - List your GitHub repositories
- `github clone <name>` - Clone a repository by name
- `github search <query>` - Search GitHub repositories

### Analytics & Statistics
- `analytics stats` - Show comprehensive repository statistics
- `analytics activity [days]` - Show commit activity over time
- `analytics files` - Show file change statistics
- `analytics branches` - Show branch activity and health
- `analytics contributors` - Show contributor statistics
- `analytics health` - Show repository health indicators

## 🎯 Detailed Usage Examples

### Repository Discovery and Setup

```bash
# Discover Git repositories in current directory
gitflow-studio --discover

# Set repository and show status
gitflow-studio --repo /path/to/my-project status

# Show repository information
gitflow-studio --repo /path/to/my-project repo info
```

### Basic Git Operations

```bash
# Show repository status
gitflow-studio --repo . status

# Show last 10 commits
gitflow-studio --repo . log --max-count 10

# Show commits with graph
gitflow-studio --repo . log --graph --oneline

# Create a new commit
gitflow-studio --repo . commit "Add new feature"

# Push changes
gitflow-studio --repo . push

# Pull latest changes
gitflow-studio --repo . pull
```

### Branch Management

```bash
# List all branches
gitflow-studio --repo . branches

# Create a new feature branch
gitflow-studio --repo . branch create feature/new-feature

# Checkout a branch
gitflow-studio --repo . checkout feature/new-feature

# Rename a branch
gitflow-studio --repo . branch rename old-branch new-branch

# Delete a local branch
gitflow-studio --repo . branch delete feature/old-feature

# Delete a remote branch
gitflow-studio --repo . branch delete-remote feature/old-feature
```

### Advanced Git Operations

```bash
# Cherry-pick a specific commit
gitflow-studio --repo . cherry-pick abc1234

# Revert a commit
gitflow-studio --repo . revert abc1234

# Interactive rebase onto main
gitflow-studio --repo . rebase-interactive main

# Squash last 3 commits
gitflow-studio --repo . squash 3
```

### Stash Operations

```bash
# Create a stash
gitflow-studio --repo . stash "Work in progress"

# List all stashes
gitflow-studio --repo . stash list

# Pop the latest stash
gitflow-studio --repo . stash pop
```

### Tag Management

```bash
# List all tags
gitflow-studio --repo . tag list

# Create a new tag
gitflow-studio --repo . tag create v1.0.0

# Show tag details
gitflow-studio --repo . tag show v1.0.0

# Delete a tag
gitflow-studio --repo . tag delete v0.9.0
```

### Git Flow Workflow

```bash
# Initialize Git Flow
gitflow-studio --repo . gitflow init

# Start a new feature
gitflow-studio --repo . gitflow feature start my-feature

# Finish a feature (merges to develop)
gitflow-studio --repo . gitflow feature finish my-feature

# Start a release
gitflow-studio --repo . gitflow release start v1.0.0

# Finish a release (merges to main and develop)
gitflow-studio --repo . gitflow release finish v1.0.0
```

### GitHub Integration

```bash
# Login to GitHub (OAuth)
gitflow-studio --repo . github login

# List your repositories
gitflow-studio --repo . github repos

# Clone a repository by name
gitflow-studio --repo . github clone my-username/my-repo

# Search repositories
gitflow-studio --repo . github search "python cli tool"

# Logout from GitHub
gitflow-studio --repo . github logout
```

### Analytics and Statistics

```bash
# Show comprehensive repository statistics
gitflow-studio --repo . analytics stats

# Show commit activity over last 30 days
gitflow-studio --repo . analytics activity 30

# Show file change statistics
gitflow-studio --repo . analytics files

# Show branch activity and health
gitflow-studio --repo . analytics branches

# Show contributor statistics
gitflow-studio --repo . analytics contributors

# Show repository health indicators
gitflow-studio --repo . analytics health
```

### Interactive Mode

```bash
# Start interactive mode
gitflow-studio --interactive

# In interactive mode, you can run commands without --repo flag:
gitflow-studio> status
gitflow-studio> log --max-count 5
gitflow-studio> branch create feature/interactive-test
gitflow-studio> analytics stats
gitflow-studio> exit
```

## 🔧 Configuration

### GitHub Authentication

GitFlow Studio uses OAuth for GitHub authentication. When you run `github login`, it will:

1. Open your browser for GitHub OAuth authorization
2. Store the access token securely using your system's keyring
3. Use the token for all GitHub API operations

### Repository Discovery

The `--discover` command automatically finds Git repositories in the current directory and subdirectories, displaying them in a formatted table.

## 📊 Analytics Features

### Repository Statistics
- Total commits, branches, tags, and files
- Repository size information
- Recent commit activity
- Current branch status

### Commit Activity
- Commit frequency over time
- Daily, weekly, and monthly patterns
- Peak activity periods
- Contributor activity trends

### File Changes
- Most modified files
- File change frequency
- File size statistics
- File type distribution

### Branch Health
- Branch activity levels
- Branch age and status
- Merge patterns
- Branch protection status

### Contributor Insights
- Top contributors
- Contribution patterns
- Activity heatmaps
- Collaboration metrics

### Repository Health
- Code quality indicators
- Documentation coverage
- Issue and PR statistics
- Overall project health score

## 🛠️ Development

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/Sherin-SEF-AI/GitFlow-Studio.git
cd GitFlow-Studio

# Install in development mode
pip install -e .

# Run tests
python -m pytest studio/tests/
```

### Project Structure

```
studio/
├── __init__.py
├── __main__.py
├── cli.py                 # Main CLI interface
├── core/                  # Core application logic
│   ├── app_context.py
│   ├── plugin_base.py
│   └── plugin_loader.py
├── db/                    # Database operations
│   └── sqlite_manager.py
├── git/                   # Git operations
│   ├── async_git.py
│   └── git_operations.py
├── github/                # GitHub integration
│   ├── auth.py
│   ├── config_template.py
│   └── repos.py
├── plugins/               # Plugin system
│   └── example_plugin.py
├── tests/                 # Test files
│   ├── test_basic.py
│   └── test_comprehensive.py
└── utils/                 # Utility functions
    └── repo_discovery.py
```

## 📝 Requirements

- **Python**: 3.9 or higher
- **Git**: For Git operations
- **Internet Connection**: For GitHub features
- **Dependencies**: Automatically installed via pip

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful CLI output
- Uses [GitPython](https://github.com/gitpython-developers/GitPython) for Git operations
- GitHub integration powered by [PyGithub](https://github.com/PyGithub/PyGithub)
- CLI framework built with [Click](https://github.com/pallets/click)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Sherin-SEF-AI/GitFlow-Studio/issues)
- **Documentation**: [FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)
- **Installation**: [PIP_INSTALLATION.md](PIP_INSTALLATION.md)

---

**Made with ❤️ by Sherin Joseph Roy** 