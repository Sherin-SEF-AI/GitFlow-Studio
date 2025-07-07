# GitFlow Studio Debian Packaging

This document explains how to build and distribute GitFlow Studio as a Debian package.

## Prerequisites

Before building the Debian package, ensure you have the required tools installed:

```bash
sudo apt update
sudo apt install build-essential devscripts python3-all python3-setuptools python3-pip
```

## Building the Package

### Quick Build

Use the provided build script:

```bash
./build-deb.sh
```

This script will:
- Clean previous builds
- Build the Debian package
- Show installation instructions

### Manual Build

If you prefer to build manually:

```bash
# Clean previous builds
rm -rf debian/gitflow-studio/
rm -rf debian/tmp/

# Build the package
dpkg-buildpackage -b -us -uc
```

## Package Structure

The Debian package includes:

- **Python Package**: Installed to `/usr/lib/python3/dist-packages/studio/`
- **CLI Executable**: Installed to `/usr/bin/gitflow-studio`
- **Documentation**: Installed to `/usr/share/doc/gitflow-studio/`

## Installation

### Install the Package

```bash
# Install the package
sudo dpkg -i ../gitflow-studio_*.deb

# Install with dependencies (recommended)
sudo apt install ../gitflow-studio_*.deb
```

### Test Installation

```bash
# Test the CLI tool
gitflow-studio --help

# Test interactive mode
gitflow-studio --interactive
```

## Dependencies

The package depends on the following Python packages:

- `python3-git` (>= 3.1.0)
- `python3-aiosqlite` (>= 0.17.0)
- `python3-aiohttp` (>= 3.8.0)
- `python3-click` (>= 8.0.0)
- `python3-rich` (>= 12.0.0)
- `python3-github` (>= 1.59.0)
- `python3-cryptography` (>= 41.0.0)
- `python3-keyring` (>= 24.0.0)

## Distribution

### Local Repository

To create a local APT repository:

```bash
# Create repository directory
mkdir -p ~/gitflow-studio-repo/conf

# Copy the package
cp ../gitflow-studio_*.deb ~/gitflow-studio-repo/

# Create repository
cd ~/gitflow-studio-repo
dpkg-scanpackages . /dev/null > Packages
gzip -k -f Packages

# Add to sources.list
echo "deb [trusted=yes] file:$(pwd) ./" | sudo tee -a /etc/apt/sources.list.d/gitflow-studio.list

# Update package list
sudo apt update
```

### PPA (Personal Package Archive)

To upload to a PPA:

1. Create a PPA on Launchpad
2. Build the source package:
   ```bash
   dpkg-buildpackage -S -us -uc
   ```
3. Upload to PPA:
   ```bash
   dput ppa:your-username/gitflow-studio ../gitflow-studio_*.changes
   ```

## Troubleshooting

### Build Errors

If you encounter build errors:

1. Check that all dependencies are installed
2. Ensure you're in the correct directory
3. Clean previous builds: `rm -rf debian/gitflow-studio/`

### Installation Issues

If installation fails:

1. Check for missing dependencies: `sudo apt install -f`
2. Verify package integrity: `dpkg -c ../gitflow-studio_*.deb`
3. Check package information: `dpkg -I ../gitflow-studio_*.deb`

### Runtime Issues

If the tool doesn't work after installation:

1. Check the executable: `which gitflow-studio`
2. Check Python path: `python3 -c "import studio; print(studio.__file__)"`
3. Check permissions: `ls -la /usr/bin/gitflow-studio`

## Version Management

To update the package version:

1. Update `pyproject.toml` version
2. Update `debian/changelog` with new version
3. Update `setup.py` version (if using)
4. Rebuild the package

## Contributing

When contributing to the packaging:

1. Test the package build process
2. Verify all dependencies are correctly specified
3. Test installation and functionality
4. Update documentation as needed 