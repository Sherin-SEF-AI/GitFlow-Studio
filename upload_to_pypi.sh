#!/bin/bash

# GitFlow Studio - PyPI Upload Script
# This script helps upload the package to PyPI

set -e

echo "🚀 GitFlow Studio - PyPI Upload Script"
echo "======================================"
echo ""

# Check if packages exist
if [ ! -f "dist/gitflow_studio-1.0.0-py3-none-any.whl" ] || [ ! -f "dist/gitflow_studio-1.0.0.tar.gz" ]; then
    echo "❌ Error: Package files not found in dist/ directory"
    echo "Please run 'python3 -m build' first to build the packages"
    exit 1
fi

echo "✅ Package files found:"
ls -la dist/
echo ""

# Check if .pypirc is configured
if [ ! -f ".pypirc" ]; then
    echo "❌ Error: .pypirc file not found"
    echo "Please create .pypirc file with your PyPI credentials"
    exit 1
fi

echo "📋 Upload Options:"
echo "1. Upload to TestPyPI (recommended for testing)"
echo "2. Upload to PyPI (production)"
echo "3. Upload to both"
echo ""

read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo "📤 Uploading to TestPyPI..."
        python3 -m twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Uploaded to TestPyPI successfully!"
        echo "🔗 TestPyPI URL: https://test.pypi.org/project/gitflow-studio/"
        echo ""
        echo "To test installation from TestPyPI:"
        echo "pip install --index-url https://test.pypi.org/simple/ gitflow-studio"
        ;;
    2)
        echo "📤 Uploading to PyPI..."
        python3 -m twine upload --repository pypi dist/*
        echo ""
        echo "✅ Uploaded to PyPI successfully!"
        echo "🔗 PyPI URL: https://pypi.org/project/gitflow-studio/"
        echo ""
        echo "Users can now install with:"
        echo "pip install gitflow-studio"
        ;;
    3)
        echo "📤 Uploading to TestPyPI..."
        python3 -m twine upload --repository testpypi dist/*
        echo ""
        echo "📤 Uploading to PyPI..."
        python3 -m twine upload --repository pypi dist/*
        echo ""
        echo "✅ Uploaded to both TestPyPI and PyPI successfully!"
        echo "🔗 TestPyPI URL: https://test.pypi.org/project/gitflow-studio/"
        echo "🔗 PyPI URL: https://pypi.org/project/gitflow-studio/"
        ;;
    *)
        echo "❌ Invalid option. Please choose 1, 2, or 3."
        exit 1
        ;;
esac

echo ""
echo "🎉 Upload completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Verify the package on PyPI/TestPyPI"
echo "2. Test installation: pip install gitflow-studio"
echo "3. Update documentation with PyPI links"
echo "4. Create GitHub release with package files" 