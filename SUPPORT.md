# Support for GitFlow Studio

## 🆘 **Getting Help**

### 📚 **Documentation**
- **[README.md](README.md)** - Main documentation and getting started guide
- **[COMMAND_REFERENCE.md](COMMAND_REFERENCE.md)** - Quick command reference
- **[FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)** - Complete feature overview
- **[PIP_INSTALLATION.md](PIP_INSTALLATION.md)** - Installation guide
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Documentation navigation

### 🐛 **Issues & Bug Reports**
- **GitHub Issues**: https://github.com/Sherin-SEF-AI/GitFlow-Studio/issues
- **Email Support**: sherin.joseph2217@gmail.com
- **Discussions**: https://github.com/Sherin-SEF-AI/GitFlow-Studio/discussions

## 🚀 **Quick Start**

### **Installation**
```bash
# Install from PyPI
pip install gitflow-studio

# Verify installation
gitflow-studio --version

# Get help
gitflow-studio --help
```

### **First Steps**
```bash
# Start interactive mode
gitflow-studio --interactive

# Discover repositories
gitflow-studio --discover

# Show repository status
gitflow-studio --status
```

## ❗ **Common Issues & Solutions**

### **1. Installation Problems**

#### **"Command not found: gitflow-studio"**
```bash
# Check if installed
pip list | grep gitflow-studio

# Reinstall if needed
pip uninstall gitflow-studio
pip install gitflow-studio

# Check PATH
echo $PATH
which gitflow-studio
```

#### **Permission Denied**
```bash
# Install for current user only
pip install --user gitflow-studio

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install gitflow-studio
```

### **2. GitHub Authentication Issues**

#### **OAuth Token Problems**
```bash
# Clear existing tokens
gitflow-studio github logout

# Re-authenticate
gitflow-studio github login
```

#### **API Rate Limits**
- GitHub has rate limits for API calls
- Wait a few minutes and try again
- Consider using a personal access token for higher limits

### **3. Repository Issues**

#### **"Not a git repository"**
```bash
# Check current directory
pwd
ls -la

# Navigate to git repository
cd /path/to/your/repo
gitflow-studio --status
```

#### **Repository Not Found**
```bash
# Check repository name
gitflow-studio github repos

# Clone specific repository
gitflow-studio github clone username/repo-name
```

### **4. Command Parsing Issues**

#### **Subcommand Not Recognized**
```bash
# Use correct syntax
gitflow-studio branch create feature-name
gitflow-studio analytics stats

# Check help for specific commands
gitflow-studio branch --help
gitflow-studio analytics --help
```

## 🔧 **Troubleshooting**

### **Debug Mode**
```bash
# Enable verbose output
gitflow-studio --verbose --help

# Check configuration
gitflow-studio --config
```

### **Log Files**
```bash
# Check application logs
ls ~/.gitflow-studio/logs/

# View recent logs
tail -f ~/.gitflow-studio/logs/app.log
```

### **Configuration Reset**
```bash
# Reset to defaults
rm -rf ~/.gitflow-studio/config.json
gitflow-studio --init
```

## 📋 **Feature-Specific Help**

### **Git Operations**
```bash
# Basic git commands
gitflow-studio --status
gitflow-studio --log
gitflow-studio --branches

# Branch management
gitflow-studio branch create feature-name
gitflow-studio branch delete feature-name
gitflow-studio checkout main
```

### **GitHub Integration**
```bash
# Authentication
gitflow-studio github login
gitflow-studio github logout

# Repository management
gitflow-studio github repos
gitflow-studio github clone repo-name
gitflow-studio github search "query"
```

### **Analytics & Statistics**
```bash
# Repository analytics
gitflow-studio analytics stats
gitflow-studio analytics activity 30
gitflow-studio analytics files
gitflow-studio analytics branches
gitflow-studio analytics contributors
gitflow-studio analytics health
```

### **Git Flow Workflow**
```bash
# Initialize Git Flow
gitflow-studio gitflow init

# Feature branches
gitflow-studio gitflow feature start feature-name
gitflow-studio gitflow feature finish feature-name

# Release branches
gitflow-studio gitflow release start 1.0.0
gitflow-studio gitflow release finish 1.0.0
```

## 🆘 **Emergency Support**

### **Critical Issues**
For critical issues affecting your workflow:

1. **Check GitHub Issues** for known problems
2. **Create a new issue** with detailed information
3. **Email support** for urgent matters

### **Issue Template**
When reporting issues, include:

```markdown
**Environment:**
- OS: [Linux/Mac/Windows]
- Python version: [3.8/3.9/3.10/3.11/3.12]
- GitFlow Studio version: [1.0.1]
- Git version: [2.x.x]

**Issue:**
- What you were trying to do
- What happened
- What you expected to happen

**Steps to reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Error messages:**
[Paste any error messages here]

**Additional context:**
[Any other relevant information]
```

## 📞 **Contact Information**

### **Primary Support**
- **Email**: sherin.joseph2217@gmail.com
- **GitHub Issues**: https://github.com/Sherin-SEF-AI/GitFlow-Studio/issues
- **Discussions**: https://github.com/Sherin-SEF-AI/GitFlow-Studio/discussions

### **Response Times**
- **Critical Issues**: Within 24 hours
- **Bug Reports**: Within 48 hours
- **Feature Requests**: Within 1 week
- **General Questions**: Within 3 days

## 🤝 **Community Support**

### **Contributing**
- **Bug Fixes**: Submit pull requests
- **Documentation**: Help improve docs
- **Feature Requests**: Open discussions
- **Testing**: Test new features

### **Resources**
- **GitHub Repository**: https://github.com/Sherin-SEF-AI/GitFlow-Studio
- **PyPI Package**: https://pypi.org/project/gitflow-studio/
- **Documentation**: https://github.com/Sherin-SEF-AI/GitFlow-Studio#readme

## 📚 **Additional Resources**

### **Git Documentation**
- [Git Official Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Flow Workflow](https://nvie.com/posts/a-successful-git-branching-model/)

### **Python Resources**
- [Python Documentation](https://docs.python.org/)
- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/)

---

**Need immediate help?** Check the [Common Issues](#-common-issues--solutions) section above, or [open an issue](https://github.com/Sherin-SEF-AI/GitFlow-Studio/issues) on GitHub! 🚀 