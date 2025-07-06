# GitFlow Studio - Installation Guide

## 🚀 Quick Start

### Prerequisites

- **Python 3.9 or higher**
- **Git** (for Git operations)
- **pip** (Python package installer)

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.9, 3.10, 3.11, or 3.12
- **Memory**: 512MB RAM minimum
- **Disk Space**: 50MB for installation

## 📦 Installation Methods

### Method 1: Install from Source (Recommended)

This is the most reliable method and ensures you get the latest features:

```bash
# Clone the repository
git clone https://github.com/Sherin-SEF-AI/GitFlow-Studio.git
cd GitFlow-Studio

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Method 2: Install with pip (Development)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install from current directory
pip install -e .
```

### Method 3: Install Dependencies Only

If you want to run without installing the package:

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python -m studio --help
```

## 🔧 Installation Options

### Global Installation (System-wide)

```bash
# Install globally (requires admin privileges)
sudo pip install -e .  # Linux/macOS
# or
pip install -e .       # Windows (run as administrator)
```

### User Installation (Recommended)

```bash
# Install for current user only
pip install --user -e .
```

### Development Installation

```bash
# Install in development mode with all dependencies
pip install -e .[dev]
```

## ✅ Verification

After installation, verify that GitFlow Studio is working:

```bash
# Check if the command is available
gitflow-studio --help

# Or run the module directly
python -m studio --help

# Test with a sample repository
gitflow-studio --discover
```

## 🎯 First Steps

### 1. Discover Repositories

```bash
# Find Git repositories in current directory
gitflow-studio --discover
```

### 2. Try Interactive Mode

```bash
# Start interactive mode
gitflow-studio --interactive
```

### 3. Basic Git Operations

```bash
# Set repository and check status
gitflow-studio --repo /path/to/your/repo status

# View commit history
gitflow-studio --repo /path/to/your/repo log --max-count 10

# List branches
gitflow-studio --repo /path/to/your/repo branch list
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Command not found: gitflow-studio"

**Solution:**
```bash
# Reinstall with proper entry points
pip uninstall gitflow-studio
pip install -e .

# Or run directly
python -m studio --help
```

#### 2. Permission Denied

**Solution:**
```bash
# Use user installation
pip install --user -e .

# Or fix permissions
sudo chown -R $USER:$USER ~/.local/bin
```

#### 3. Python Version Issues

**Solution:**
```bash
# Check Python version
python --version

# Should be 3.9 or higher
# If not, install Python 3.9+
```

#### 4. Missing Dependencies

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Virtual Environment Issues

**Solution:**
```bash
# Create fresh virtual environment
python -m venv venv_new
source venv_new/bin/activate  # Linux/macOS
# or
venv_new\Scripts\activate     # Windows

# Reinstall
pip install -e .
```

### Platform-Specific Issues

#### Linux

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-venv python3-pip git

# Install system dependencies (CentOS/RHEL)
sudo yum install python3-venv python3-pip git
```

#### macOS

```bash
# Install with Homebrew
brew install python3 git

# Or with MacPorts
sudo port install python39 py39-pip git
```

#### Windows

```bash
# Install Python from python.org
# Install Git from git-scm.com

# Use PowerShell or Command Prompt
# Make sure Python and Git are in PATH
```

## 🔍 Dependencies

### Core Dependencies

- **GitPython** (>=3.1.0) - Git operations
- **aiosqlite** (>=0.17.0) - Async SQLite database
- **aiohttp** (>=3.8.0) - Async HTTP client
- **click** (>=8.0.0) - CLI framework
- **rich** (>=12.0.0) - Beautiful terminal output

### Optional Dependencies

- **git-flow** - For Git Flow operations (install separately)
- **git** - Git command line tools

## 📁 Directory Structure

After installation, the package structure is:

```
gitflow-studio/
├── studio/
│   ├── __init__.py
│   ├── cli.py              # Main CLI interface
│   ├── core/               # Core functionality
│   ├── git/                # Git operations
│   ├── plugins/            # Plugin system
│   └── utils/              # Utilities
├── setup.py               # Installation script
├── requirements.txt       # Dependencies
├── README.md             # Documentation
└── LICENSE               # License file
```

## 🚀 Advanced Installation

### Custom Installation Path

```bash
# Install to custom directory
pip install -e . --target /custom/path

# Add to PATH
export PATH="/custom/path/bin:$PATH"
```

### Development Installation

```bash
# Install with development dependencies
pip install -e .[dev]

# Install additional development tools
pip install pytest black flake8 mypy
```

### Docker Installation

```dockerfile
# Dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y git
WORKDIR /app
COPY . .
RUN pip install -e .

ENTRYPOINT ["gitflow-studio"]
```

## 🔧 Configuration

### Environment Variables

```bash
# Set custom configuration
export GITFLOW_STUDIO_CONFIG_PATH="/path/to/config"
export GITFLOW_STUDIO_LOG_LEVEL="DEBUG"
```

### Configuration File

Create `~/.gitflow-studio/config.yaml`:

```yaml
# GitFlow Studio Configuration
default_repository: ~/projects
log_level: INFO
plugins:
  enabled: true
  auto_load: true
```

## 📚 Next Steps

After successful installation:

1. **Read the README** for usage examples
2. **Try interactive mode** with `gitflow-studio --interactive`
3. **Discover repositories** with `gitflow-studio --discover`
4. **Explore features** with `gitflow-studio --help`

## 🆘 Getting Help

- **Documentation**: Check the README.md file
- **Issues**: Report problems on GitHub Issues
- **Community**: Join discussions on GitHub Discussions
- **Examples**: See the test files for usage examples

## 🔄 Updating

To update GitFlow Studio:

```bash
# If installed from source
cd gitflow-studio
git pull
pip install -e .

# If installed from PyPI (when available)
pip install --upgrade gitflow-studio
```

## 🧹 Uninstalling

To remove GitFlow Studio:

```bash
# Remove the package
pip uninstall gitflow-studio

# Remove configuration files (optional)
rm -rf ~/.gitflow-studio
```

---

**Happy Git workflow management! 🎉** 