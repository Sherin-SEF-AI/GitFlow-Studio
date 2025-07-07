# GitFlow Studio - Command Reference

## 🚀 Quick Start Commands

```bash
# Install
pip install gitflow-studio

# Help
gitflow-studio --help

# Interactive mode
gitflow-studio --interactive

# Discover repositories
gitflow-studio --discover
```

## 📋 All Commands

### Repository Management
| Command | Description | Example |
|---------|-------------|---------|
| `discover` | Find Git repositories | `gitflow-studio --discover` |
| `repo info` | Show repository info | `gitflow-studio --repo . repo info` |

### Git Operations
| Command | Description | Example |
|---------|-------------|---------|
| `status` | Show repository status | `gitflow-studio --repo . status` |
| `log` | Show commit log | `gitflow-studio --repo . log --max-count 10` |
| `branches` | List all branches | `gitflow-studio --repo . branches` |
| `checkout <ref>` | Checkout branch/commit | `gitflow-studio --repo . checkout main` |
| `commit <message>` | Create commit | `gitflow-studio --repo . commit "Add feature"` |
| `push` | Push changes | `gitflow-studio --repo . push` |
| `pull` | Pull changes | `gitflow-studio --repo . pull` |

### Branch Management
| Command | Description | Example |
|---------|-------------|---------|
| `branch create <name>` | Create new branch | `gitflow-studio --repo . branch create feature/new` |
| `branch delete <name>` | Delete local branch | `gitflow-studio --repo . branch delete feature/old` |
| `branch delete-remote <name>` | Delete remote branch | `gitflow-studio --repo . branch delete-remote feature/old` |
| `branch rename <old> <new>` | Rename branch | `gitflow-studio --repo . branch rename old new` |

### Advanced Git Operations
| Command | Description | Example |
|---------|-------------|---------|
| `cherry-pick <hash>` | Cherry-pick commit | `gitflow-studio --repo . cherry-pick abc1234` |
| `revert <hash>` | Revert commit | `gitflow-studio --repo . revert abc1234` |
| `rebase-interactive <base>` | Interactive rebase | `gitflow-studio --repo . rebase-interactive main` |
| `squash <count>` | Squash commits | `gitflow-studio --repo . squash 3` |

### Stash Operations
| Command | Description | Example |
|---------|-------------|---------|
| `stash [message]` | Create stash | `gitflow-studio --repo . stash "WIP"` |
| `stash list` | List stashes | `gitflow-studio --repo . stash list` |
| `stash pop` | Pop latest stash | `gitflow-studio --repo . stash pop` |

### Tag Operations
| Command | Description | Example |
|---------|-------------|---------|
| `tag list` | List all tags | `gitflow-studio --repo . tag list` |
| `tag create <name>` | Create tag | `gitflow-studio --repo . tag create v1.0.0` |
| `tag delete <name>` | Delete tag | `gitflow-studio --repo . tag delete v0.9.0` |
| `tag show <name>` | Show tag details | `gitflow-studio --repo . tag show v1.0.0` |

### Git Flow Operations
| Command | Description | Example |
|---------|-------------|---------|
| `gitflow init` | Initialize Git Flow | `gitflow-studio --repo . gitflow init` |
| `gitflow feature start <name>` | Start feature | `gitflow-studio --repo . gitflow feature start my-feature` |
| `gitflow feature finish <name>` | Finish feature | `gitflow-studio --repo . gitflow feature finish my-feature` |
| `gitflow release start <version>` | Start release | `gitflow-studio --repo . gitflow release start v1.0.0` |
| `gitflow release finish <version>` | Finish release | `gitflow-studio --repo . gitflow release finish v1.0.0` |

### GitHub Operations
| Command | Description | Example |
|---------|-------------|---------|
| `github login` | Login to GitHub | `gitflow-studio --repo . github login` |
| `github logout` | Logout from GitHub | `gitflow-studio --repo . github logout` |
| `github repos` | List repositories | `gitflow-studio --repo . github repos` |
| `github clone <name>` | Clone repository | `gitflow-studio --repo . github clone user/repo` |
| `github search <query>` | Search repositories | `gitflow-studio --repo . github search "python"` |

### Analytics & Statistics
| Command | Description | Example |
|---------|-------------|---------|
| `analytics stats` | Repository statistics | `gitflow-studio --repo . analytics stats` |
| `analytics activity [days]` | Commit activity | `gitflow-studio --repo . analytics activity 30` |
| `analytics files` | File statistics | `gitflow-studio --repo . analytics files` |
| `analytics branches` | Branch health | `gitflow-studio --repo . analytics branches` |
| `analytics contributors` | Contributor stats | `gitflow-studio --repo . analytics contributors` |
| `analytics health` | Repository health | `gitflow-studio --repo . analytics health` |

## 🎯 Common Workflows

### New Feature Development
```bash
# 1. Start feature branch
gitflow-studio --repo . gitflow feature start new-feature

# 2. Make changes and commit
gitflow-studio --repo . commit "Add new feature"

# 3. Push feature branch
gitflow-studio --repo . push

# 4. Finish feature (merges to develop)
gitflow-studio --repo . gitflow feature finish new-feature
```

### Release Management
```bash
# 1. Start release
gitflow-studio --repo . gitflow release start v1.0.0

# 2. Make release fixes
gitflow-studio --repo . commit "Fix release issues"

# 3. Finish release (merges to main and develop)
gitflow-studio --repo . gitflow release finish v1.0.0

# 4. Create tag
gitflow-studio --repo . tag create v1.0.0
```

### Repository Analysis
```bash
# 1. Get overview
gitflow-studio --repo . analytics stats

# 2. Check activity
gitflow-studio --repo . analytics activity 30

# 3. Review contributors
gitflow-studio --repo . analytics contributors

# 4. Assess health
gitflow-studio --repo . analytics health
```

## 🔧 Interactive Mode Commands

In interactive mode (`gitflow-studio --interactive`), you can use commands without the `--repo` flag:

```bash
gitflow-studio> status
gitflow-studio> log --max-count 5
gitflow-studio> branch create feature/test
gitflow-studio> analytics stats
gitflow-studio> help
gitflow-studio> exit
```

## 📊 Log Options

```bash
# Basic log
gitflow-studio --repo . log

# Limited commits
gitflow-studio --repo . log --max-count 10

# With graph
gitflow-studio --repo . log --graph --oneline

# Since date
gitflow-studio --repo . log --since "2024-01-01"

# Author filter
gitflow-studio --repo . log --author "John Doe"
```

## 🏷️ Tag Options

```bash
# List tags
gitflow-studio --repo . tag list

# Create annotated tag
gitflow-studio --repo . tag create v1.0.0

# Show tag details
gitflow-studio --repo . tag show v1.0.0

# Delete tag
gitflow-studio --repo . tag delete v0.9.0
```

## 🌊 Git Flow Branches

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature development branches
- `release/*` - Release preparation branches
- `hotfix/*` - Critical bug fixes

## 📈 Analytics Insights

### Repository Statistics
- Total commits, branches, tags, files
- Repository size and structure
- Recent activity patterns

### Commit Activity
- Daily/weekly/monthly patterns
- Peak activity periods
- Contributor trends

### File Changes
- Most modified files
- File change frequency
- File type distribution

### Branch Health
- Branch activity levels
- Age and status
- Merge patterns

### Contributor Insights
- Top contributors
- Activity heatmaps
- Collaboration metrics

### Repository Health
- Code quality indicators
- Documentation coverage
- Overall health score

---

**Quick Tip**: Use `gitflow-studio --help` for detailed command options and `gitflow-studio --interactive` for an easier experience! 