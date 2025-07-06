# Contributing to gitflow-studio

Thank you for your interest in contributing to gitflow-studio! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Plugin Development](#plugin-development)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- PyQt6 development libraries
- QScintilla development libraries

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/gitflow-studio.git
   cd gitflow-studio
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install in development mode:
   ```bash
   pip install -e .
   ```

## Development Setup

### Running the Application

```bash
python -m studio
```

### Building the Debian Package

```bash
# Install build dependencies
sudo apt-get install build-essential devscripts debhelper

# Build the package
dpkg-buildpackage -b -us -uc
```

### Development Tools

- **IDE**: We recommend using VS Code or PyCharm with Python and Qt support
- **Debugging**: Use Python's built-in debugger or IDE debugging features
- **Linting**: We use flake8 for code linting
- **Formatting**: We use black for code formatting

## Project Structure

```
gitflow-studio/
├── studio/                    # Main application package
│   ├── core/                 # Core application logic
│   │   ├── app_context.py    # Application context and state management
│   │   └── plugin_loader.py  # Plugin system
│   ├── gui/                  # User interface components
│   │   ├── main_window.py    # Main application window
│   │   ├── repository_dashboard.py  # Repository management UI
│   │   ├── git_graph_widget.py      # Visual Git graph
│   │   └── dialogs/          # Dialog windows
│   ├── git/                  # Git operations
│   │   ├── async_git.py      # Async Git wrapper
│   │   └── git_operations.py # Comprehensive Git operations
│   ├── plugins/              # Built-in plugins
│   ├── db/                   # Database management
│   └── utils/                # Utility modules
│       ├── theme_manager.py  # Theme management
│       ├── analytics.py      # Usage analytics
│       ├── security.py       # Security features
│       └── repo_discovery.py # Repository discovery
├── resources/                # Application resources
├── debian/                   # Debian packaging files
├── tests/                    # Test suite
└── docs/                     # Documentation
```

## Plugin Development

### Creating a Plugin

1. Create a new Python file in `studio/plugins/` or your custom plugins directory
2. Implement the required interface:

```python
def register(app_context):
    """Register the plugin with the application context"""
    # Add your plugin functionality here
    print("My plugin loaded!")
    
    # Example: Add a menu item
    # app_context.add_menu_item("Tools", "My Plugin", my_plugin_action)
```

### Plugin Interface

Plugins can:
- Add menu items and toolbars
- Extend Git operations
- Add new UI components
- Integrate with external services
- Customize themes and styling

### Example Plugin

```python
from PyQt6.QtWidgets import QAction, QMessageBox

def my_plugin_action(app_context):
    """Example plugin action"""
    QMessageBox.information(None, "Plugin", "Hello from my plugin!")

def register(app_context):
    """Register the example plugin"""
    # Add menu action
    action = QAction("Example Plugin", None)
    action.triggered.connect(lambda: my_plugin_action(app_context))
    
    # Add to application menu
    app_context.add_menu_action("Tools", action)
```

## Testing

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_comprehensive

# Run with coverage
coverage run -m unittest discover tests
coverage report
```

### Writing Tests

- Place test files in the `tests/` directory
- Use descriptive test method names
- Include both unit tests and integration tests
- Mock external dependencies when appropriate
- Test both success and failure scenarios

### Test Structure

```python
import unittest
from unittest.mock import Mock, patch

class TestMyComponent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        pass
        
    def tearDown(self):
        """Clean up after tests"""
        pass
        
    def test_something(self):
        """Test description"""
        # Test implementation
        self.assertTrue(True)
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:
- Line length: 88 characters (black default)
- Use type hints where appropriate
- Use f-strings for string formatting
- Use async/await for asynchronous operations

### Qt/PyQt6 Guidelines

- Use PyQt6 for all GUI components
- Follow Qt naming conventions
- Use signals and slots for communication
- Handle Qt events properly

### Code Formatting

```bash
# Format code with black
black studio/ tests/

# Check code style with flake8
flake8 studio/ tests/
```

## Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the code style guidelines
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Run tests** to ensure everything works
6. **Submit a pull request** with a clear description

### Pull Request Guidelines

- Use descriptive commit messages
- Include a summary of changes
- Reference related issues
- Ensure all tests pass
- Update documentation if needed

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

## Reporting Issues

### Bug Reports

When reporting bugs, please include:
- Operating system and version
- Python version
- gitflow-studio version
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs

### Feature Requests

For feature requests:
- Describe the feature clearly
- Explain the use case
- Consider implementation complexity
- Check if similar features exist

### Issue Templates

Use the provided issue templates for:
- Bug reports
- Feature requests
- Plugin requests
- Documentation improvements

## Development Workflow

### Daily Development

1. Pull latest changes from main branch
2. Create feature branch for your work
3. Make changes and test locally
4. Commit with descriptive messages
5. Push and create pull request

### Release Process

1. Update version numbers
2. Update changelog
3. Run full test suite
4. Build and test packages
5. Create release tag
6. Deploy packages

## Getting Help

- **Documentation**: Check the docs/ directory
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Chat**: Join our community chat (if available)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read our Code of Conduct for details.

## License

By contributing to gitflow-studio, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to gitflow-studio! 