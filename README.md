# GitFlow Studio CLI

A comprehensive Git workflow management CLI tool for developers who prefer command-line interfaces.

**Author:** Sherin Joseph Roy  
**Email:** sherin.joseph2217@gmail.com  
**Repository:** [https://github.com/Sherin-SEF-AI/GitFlow-Studio](https://github.com/Sherin-SEF-AI/GitFlow-Studio)

## Features

- **Git Operations**: Status, log, branches, commits, push/pull
- **Branch Management**: Create, checkout, merge, rebase
- **Stash Operations**: Create, list, apply, pop stashes
- **Git Flow Workflow**: Initialize and manage Git Flow branches
- **Plugin System**: Extensible architecture for custom workflows
- **Async Operations**: Non-blocking Git operations
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Installation

### Quick Install (Recommended)

#### Linux/macOS
```bash
# Clone the repository
git clone https://github.com/Sherin-SEF-AI/GitFlow-Studio.git
cd GitFlow-Studio

# Run the installation script
./install.sh
```

#### Windows
```cmd
# Clone the repository
git clone https://github.com/Sherin-SEF-AI/GitFlow-Studio.git
cd GitFlow-Studio

# Run the installation script
install.bat
```

### Manual Installation

#### From Source
```bash
# Clone the repository
git clone https://github.com/Sherin-SEF-AI/GitFlow-Studio.git
cd GitFlow-Studio

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

#### From PyPI (when available)
```bash
pip install gitflow-studio
```

### Prerequisites
- **Python 3.9 or higher**
- **Git** (for Git operations)
- **pip** (Python package installer)

For detailed installation instructions and troubleshooting, see [INSTALLATION.md](INSTALLATION.md).

## Usage

### Basic Commands

```bash
# Set repository and show status
gitflow-studio --repo /path/to/repo status

# Show commit log
gitflow-studio --repo /path/to/repo log --max-count 10

# List all branches
gitflow-studio --repo /path/to/repo branch list

# Create a new branch
gitflow-studio --repo /path/to/repo branch create feature/new-feature

# Checkout a branch
gitflow-studio --repo /path/to/repo branch checkout feature/new-feature

# Merge a branch
gitflow-studio --repo /path/to/repo branch merge feature/new-feature

# Rebase current branch
gitflow-studio --repo /path/to/repo branch rebase main
```

### Stash Operations

```bash
# List stashes
gitflow-studio --repo /path/to/repo stash list

# Create a stash
gitflow-studio --repo /path/to/repo stash create --message "WIP: feature in progress"

# Pop a stash
gitflow-studio --repo /path/to/repo stash pop --ref stash@{0}
```

### Commit and Push/Pull

```bash
# Create a commit
gitflow-studio --repo /path/to/repo commit "Add new feature" --add-all

# Push changes
gitflow-studio --repo /path/to/repo push

# Pull changes
gitflow-studio --repo /path/to/repo pull
```

### Git Flow Workflow

```bash
# Initialize Git Flow
gitflow-studio --repo /path/to/repo gitflow init

# Start a feature branch
gitflow-studio --repo /path/to/repo gitflow feature-start my-feature

# Finish a feature branch
gitflow-studio --repo /path/to/repo gitflow feature-finish my-feature

# Start a release
gitflow-studio --repo /path/to/repo gitflow release-start v1.0.0

# Finish a release
gitflow-studio --repo /path/to/repo gitflow release-finish v1.0.0
```

## Configuration

The tool uses the existing Git configuration in your repository. No additional configuration is required.

## Development

### Prerequisites

- Python 3.9+
- Git

### Setup Development Environment

```bash
git clone https://github.com/Sherin-SEF-AI/GitFlow-Studio.git
cd GitFlow-Studio
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Running Tests

```bash
python test_features.py
```

## Architecture

- **CLI Interface**: Command-line interface using argparse
- **Git Operations**: Async Git operations using GitPython
- **Plugin System**: Extensible plugin architecture
- **Database**: SQLite for storing repository metadata
- **Async Support**: Full async/await support for non-blocking operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- Issues: [GitHub Issues](https://github.com/Sherin-SEF-AI/GitFlow-Studio/issues)
- Documentation: [GitHub Wiki](https://github.com/Sherin-SEF-AI/GitFlow-Studio/wiki) 