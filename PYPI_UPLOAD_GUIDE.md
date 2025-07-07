# GitFlow Studio - PyPI Upload Guide

## 🚀 Uploading to PyPI

This guide will help you upload GitFlow Studio to the Python Package Index (PyPI) for public distribution.

## 📋 Prerequisites

### 1. PyPI Account
- Create an account at [PyPI](https://pypi.org/account/register/)
- Enable two-factor authentication (recommended)

### 2. API Token
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Click "Add API token"
3. Give it a name (e.g., "GitFlow Studio Upload")
4. Select "Entire account (all projects)"
5. Copy the token (starts with `pypi-`)

### 3. TestPyPI Account (Optional)
- Create an account at [TestPyPI](https://test.pypi.org/account/register/)
- Get an API token from TestPyPI as well

## 🔧 Setup

### 1. Configure Authentication

Create a `.pypirc` file in your project root:

```bash
# Create .pypirc file
cat > .pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = YOUR_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = YOUR_TEST_PYPI_TOKEN_HERE
EOF
```

**Replace `YOUR_PYPI_TOKEN_HERE` with your actual PyPI token.**

### 2. Verify Package

```bash
# Check if packages are valid
python3 -m twine check dist/*

# Should show: PASSED for both files
```

## 📤 Upload Process

### Option 1: Using the Upload Script (Recommended)

```bash
# Run the upload script
./upload_to_pypi.sh

# Follow the interactive prompts
```

### Option 2: Manual Upload

#### Upload to TestPyPI (Testing)
```bash
# Upload to TestPyPI first (recommended)
python3 -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ gitflow-studio
```

#### Upload to PyPI (Production)
```bash
# Upload to PyPI
python3 -m twine upload --repository pypi dist/*

# Verify installation
pip install gitflow-studio
```

## 🔍 Verification

### 1. Check PyPI Listing
- Visit: https://pypi.org/project/gitflow-studio/
- Verify package information is correct
- Check that README renders properly

### 2. Test Installation
```bash
# Create a new virtual environment for testing
python3 -m venv test_env
source test_env/bin/activate

# Install from PyPI
pip install gitflow-studio

# Test the command
gitflow-studio --help

# Test basic functionality
gitflow-studio --discover
```

### 3. Verify Package Contents
```bash
# Check what's installed
pip show gitflow-studio

# List installed files
pip show -f gitflow-studio
```

## 📝 Package Information

### Current Package Details
- **Name**: `gitflow-studio`
- **Version**: `1.0.0`
- **Author**: Sherin Joseph Roy
- **License**: MIT
- **Python**: >=3.9
- **Homepage**: https://github.com/Sherin-SEF-AI/GitFlow-Studio

### Package Files
- `gitflow_studio-1.0.0-py3-none-any.whl` (Wheel)
- `gitflow_studio-1.0.0.tar.gz` (Source)

## 🚨 Important Notes

### Version Management
- **Never upload the same version twice** to PyPI
- Increment version in `pyproject.toml` for new releases
- Use semantic versioning (e.g., 1.0.1, 1.1.0, 2.0.0)

### Package Name
- The package name `gitflow-studio` is now reserved
- Make sure it's available before uploading
- Check: https://pypi.org/project/gitflow-studio/

### Documentation
- PyPI will automatically render the README.md
- Ensure README.md is properly formatted
- Include installation and usage instructions

## 🔄 Update Process

For future updates:

1. **Update version** in `pyproject.toml`
2. **Rebuild packages**:
   ```bash
   python3 -m build
   ```
3. **Upload new version**:
   ```bash
   python3 -m twine upload --repository pypi dist/*
   ```

## 🛠️ Troubleshooting

### Common Issues

#### "File already exists"
- **Cause**: Version already uploaded
- **Solution**: Increment version number

#### "Authentication failed"
- **Cause**: Invalid API token
- **Solution**: Check `.pypirc` configuration

#### "Package validation failed"
- **Cause**: Package metadata issues
- **Solution**: Run `python3 -m twine check dist/*`

#### "README not rendering"
- **Cause**: Markdown formatting issues
- **Solution**: Test README.md locally

### Getting Help
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)

## 📊 Post-Upload Checklist

- [ ] Package appears on PyPI
- [ ] README renders correctly
- [ ] Installation works: `pip install gitflow-studio`
- [ ] Command works: `gitflow-studio --help`
- [ ] Basic functionality tested
- [ ] Documentation updated with PyPI links
- [ ] GitHub release created
- [ ] Social media announcement (optional)

## 🎉 Success!

Once uploaded successfully, users can install GitFlow Studio with:

```bash
pip install gitflow-studio
```

And use it immediately:

```bash
gitflow-studio --help
gitflow-studio --interactive
```

---

**Congratulations! GitFlow Studio is now available on PyPI! 🚀** 