#!/bin/bash

# GitFlow Studio Debian Package Builder
# This script builds a Debian package for GitFlow Studio

set -e

echo "🚀 Building GitFlow Studio Debian Package..."

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -d "debian" ]; then
    echo "❌ Error: This script must be run from the GitFlow Studio root directory"
    exit 1
fi

# Check if required tools are installed
if ! command -v dpkg-buildpackage &> /dev/null; then
    echo "❌ Error: dpkg-buildpackage is not installed. Please install build-essential and devscripts:"
    echo "   sudo apt install build-essential devscripts"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf debian/gitflow-studio/
rm -rf debian/tmp/
rm -f ../gitflow-studio_*.deb
rm -f ../gitflow-studio_*.dsc
rm -f ../gitflow-studio_*.tar.gz
rm -f ../gitflow-studio_*.buildinfo
rm -f ../gitflow-studio_*.changes

# Build the package
echo "🔨 Building Debian package..."
dpkg-buildpackage -b -us -uc

echo "✅ Package built successfully!"
echo ""
echo "📦 Generated files:"
ls -la ../gitflow-studio_*

echo ""
echo "📋 To install the package:"
echo "   sudo dpkg -i ../gitflow-studio_*.deb"
echo ""
echo "📋 To install with dependencies:"
echo "   sudo apt install ../gitflow-studio_*.deb"
echo ""
echo "📋 To test the installation:"
echo "   gitflow-studio --help" 