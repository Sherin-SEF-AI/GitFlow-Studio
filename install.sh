#!/bin/bash

# GitFlow Studio Installation Script
# This script installs GitFlow Studio using pip

set -e

echo "🚀 Installing GitFlow Studio..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $python_version is installed, but Python $required_version or higher is required."
    exit 1
fi

echo "✅ Python $python_version detected"

# Install GitFlow Studio
echo "📦 Installing GitFlow Studio..."
pip3 install gitflow-studio

echo ""
echo "✅ GitFlow Studio installed successfully!"
echo ""
echo "🎉 You can now use GitFlow Studio with the following commands:"
echo "   gitflow-studio --help"
echo "   gitflow-studio --interactive"
echo "   gitflow-studio --repo /path/to/repo status"
echo ""
echo "📚 For more information, visit:"
echo "   https://github.com/Sherin-SEF-AI/GitFlow-Studio" 