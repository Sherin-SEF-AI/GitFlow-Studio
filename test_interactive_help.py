#!/usr/bin/env python3
"""
Test script to verify interactive mode help includes GitHub commands
"""

import sys
from pathlib import Path

# Add the studio directory to the path
sys.path.insert(0, str(Path(__file__).parent / "studio"))

from studio.cli import GitFlowStudioCLI

def test_interactive_help():
    """Test that interactive help includes GitHub commands"""
    cli = GitFlowStudioCLI()
    
    # Capture the help output
    import io
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        cli.show_interactive_help()
    
    help_output = f.getvalue()
    
    # Check for GitHub commands
    github_commands = [
        "github login",
        "github logout", 
        "github repos",
        "github clone",
        "github search"
    ]
    
    missing_commands = []
    for cmd in github_commands:
        if cmd not in help_output:
            missing_commands.append(cmd)
    
    if missing_commands:
        print(f"❌ Missing GitHub commands in help: {missing_commands}")
        return False
    else:
        print("✅ All GitHub commands found in interactive help")
        return True

if __name__ == "__main__":
    print("🧪 Testing Interactive Mode Help")
    print("=" * 40)
    
    success = test_interactive_help()
    
    if success:
        print("\n✅ Interactive help test passed!")
    else:
        print("\n❌ Interactive help test failed!")
        sys.exit(1) 