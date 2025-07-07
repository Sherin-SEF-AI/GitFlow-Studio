# GitFlow Studio - Pip Installation Guide

## Quick Installation

Install GitFlow Studio directly from PyPI using pip:

```bash
pip install gitflow-studio
```

Or using the installation script:

```bash
curl -sSL https://raw.githubusercontent.com/Sherin-SEF-AI/GitFlow-Studio/main/install.sh | bash
```

## Requirements

- Python 3.9 or higher
- Git (for Git operations)
- Internet connection (for GitHub features)

## Usage

After installation, you can use GitFlow Studio with the `gitflow-studio` command:

```bash
# Show help
gitflow-studio --help

# Run in interactive mode
gitflow-studio --interactive

# Show repository status
gitflow-studio --repo /path/to/repo status

# Show commit log
gitflow-studio --repo /path/to/repo log --max-count 10

# Create a new branch
gitflow-studio --repo /path/to/repo branch create feature/new-feature

# Initialize Git Flow
gitflow-studio --repo /path/to/repo gitflow init

# Show repository analytics
gitflow-studio --repo /path/to/repo analytics stats
```

## Features

GitFlow Studio includes:

- **Git Operations**: Status, log, commit, push, pull, branch management
- **Git Flow**: Feature, release, and hotfix branch management
- **GitHub Integration**: Repository listing, cloning, search
- **Advanced Features**: Cherry-pick, revert, interactive rebase, squash
- **Analytics**: Repository statistics, commit activity, contributor stats
- **Interactive Mode**: User-friendly command-line interface

## Uninstallation

To uninstall GitFlow Studio:

```bash
pip uninstall gitflow-studio
```

## Development Installation

For development or local installation:

```bash
# Clone the repository
git clone https://github.com/Sherin-SEF-AI/GitFlow-Studio.git
cd GitFlow-Studio

# Install in development mode
pip install -e .
```

## Support

- **Documentation**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/Sherin-SEF-AI/GitFlow-Studio/issues)
- **Features**: [FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)

## License

MIT License - see [LICENSE](LICENSE) file for details. 