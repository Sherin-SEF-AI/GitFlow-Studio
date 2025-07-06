#!/bin/bash

# GitFlow Studio Installation Script
# This script installs GitFlow Studio with all dependencies

set -e  # Exit on any error

echo "🚀 GitFlow Studio Installation Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
        
        # Check if version is 3.9 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
            print_success "Python version is compatible (3.9+)"
        else
            print_error "Python version must be 3.9 or higher. Current version: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    elif python3 -m pip --version &> /dev/null; then
        print_success "pip found (via python3 -m pip)"
    else
        print_error "pip is not installed. Please install pip."
        exit 1
    fi
}

# Check if Git is installed
check_git() {
    print_status "Checking Git installation..."
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_success "Git $GIT_VERSION found"
    else
        print_error "Git is not installed. Please install Git."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    print_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install the package in development mode
    pip install -e .
    
    print_success "Dependencies installed successfully"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    if command -v gitflow-studio &> /dev/null; then
        print_success "gitflow-studio command is available"
    else
        print_warning "gitflow-studio command not found in PATH, but you can run with: python -m studio"
    fi
    
    # Test the module directly
    if python -m studio --help &> /dev/null; then
        print_success "GitFlow Studio is working correctly"
    else
        print_error "GitFlow Studio installation test failed"
        exit 1
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎉 Installation completed successfully!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Try GitFlow Studio:"
    echo "   gitflow-studio --help"
    echo "   gitflow-studio --discover"
    echo "   gitflow-studio --interactive"
    echo ""
    echo "3. Basic usage:"
    echo "   gitflow-studio --repo /path/to/repo status"
    echo "   gitflow-studio --repo /path/to/repo log --max-count 10"
    echo ""
    echo "For more information, see:"
    echo "- README.md - Basic usage and examples"
    echo "- INSTALLATION.md - Detailed installation guide"
    echo "- FEATURE_SUMMARY.md - Complete feature overview"
    echo ""
}

# Main installation process
main() {
    echo "Starting GitFlow Studio installation..."
    echo ""
    
    # Check prerequisites
    check_python
    check_pip
    check_git
    
    # Create and activate virtual environment
    create_venv
    activate_venv
    
    # Install dependencies
    install_dependencies
    
    # Test installation
    test_installation
    
    # Show next steps
    show_next_steps
}

# Run main function
main "$@" 