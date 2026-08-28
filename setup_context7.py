#!/usr/bin/env python3
"""
Context7 MCP Setup Script
Automates installation and initialization of Context7 MCP
"""

import os
import sys
import subprocess
import json
import platform
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color


def print_status(msg):
    """Print success status"""
    print(f"{Colors.GREEN}✓{Colors.NC} {msg}")


def print_info(msg):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ{Colors.NC} {msg}")


def print_warning(msg):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {msg}")


def print_error(msg):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.NC} {msg}")


def check_command(cmd):
    """Check if a command exists in PATH"""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def install_context7():
    """Install Context7"""
    print("Choose installation method:")
    print("1) pip (Python package manager - recommended)")
    print("2) npm (Node package manager)")
    print("3) Manual installation (skip)")
    print()

    choice = input("Enter your choice [1-3]: ").strip()

    if choice == "1":
        print_info("Installing Context7 via pip...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "context7"],
                check=True
            )
            print_status("Context7 installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Installation failed: {e}")
            return False

    elif choice == "2":
        print_info("Installing Context7 via npm...")
        try:
            subprocess.run(["npm", "install", "-g", "context7"], check=True)
            print_status("Context7 installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Installation failed: {e}")
            return False

    elif choice == "3":
        print_warning("Skipping installation")
        print("Please install Context7 manually:")
        print("  pip install context7")
        return False

    else:
        print_error("Invalid choice")
        return False


def verify_context7():
    """Verify Context7 is installed"""
    if not check_command("context7"):
        return False

    try:
        result = subprocess.run(
            ["context7", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print_status(f"Context7 verified: {result.stdout.strip()}")
        return True
    except Exception as e:
        print_error(f"Failed to verify Context7: {e}")
        return False


def setup_claude_directory():
    """Setup .claude directory and configuration files"""
    claude_dir = Path(".claude")

    print_info("Checking .claude directory...")
    if not claude_dir.exists():
        claude_dir.mkdir(parents=True, exist_ok=True)
        print_status("Created .claude directory")
    else:
        print_status(".claude directory exists")

    # Check MCP configuration
    mcp_config_path = claude_dir / "mcp.json"
    if mcp_config_path.exists():
        print_status(".claude/mcp.json exists")
    else:
        print_warning(".claude/mcp.json not found - it should be in the repo")

    settings_path = claude_dir / "settings.json"
    if settings_path.exists():
        print_status(".claude/settings.json exists")
    else:
        print_warning(".claude/settings.json not found - it should be in the repo")


def test_mcp_server():
    """Test if Context7 MCP server can start"""
    print_info("Testing Context7 MCP server...")

    try:
        # Try to start the server with a timeout
        process = subprocess.Popen(
            ["context7", "mcp", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for 3 seconds
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            # This is expected - the server keeps running
            process.terminate()
            print_status("MCP server test passed (server is running)")
            return True

    except FileNotFoundError:
        print_warning("Could not test MCP server (Context7 not in PATH)")
        return False
    except Exception as e:
        print_warning(f"MCP server test inconclusive: {e}")
        return False


def print_summary():
    """Print setup summary and next steps"""
    print()
    print("=" * 50)
    print(f"{Colors.GREEN}Setup Complete!{Colors.NC}")
    print("=" * 50)
    print()
    print("Next steps:")
    print()
    print("1. Open this project in Claude Code:")
    print(f"   {Colors.BLUE}claude code .{Colors.NC}")
    print()
    print("2. Or open in Claude Desktop:")
    print(f"   {Colors.BLUE}File → Open Folder → select markitdown{Colors.NC}")
    print()
    print("3. Try using Context7 with a prompt:")
    print(f"   {Colors.BLUE}Use Context7 to extract text from README.md{Colors.NC}")
    print()
    print(f"For detailed usage guide, see: {Colors.BLUE}CONTEXT7_MCP_GUIDE.md{Colors.NC}")
    print()
    print_status("All set! Happy coding! 🎉")
    print()


def main():
    """Main setup routine"""
    print()
    print("=" * 50)
    print("  Context7 MCP Setup Script")
    print("=" * 50)
    print()

    # Step 1: Check/Install Context7
    print("Step 1: Checking Context7 installation...")
    if not check_command("context7"):
        print_warning("Context7 not found")
        if not install_context7():
            print_error("Cannot proceed without Context7")
            sys.exit(1)

    print()

    # Step 2: Verify Context7
    print("Step 2: Verifying Context7...")
    if not verify_context7():
        print_error("Cannot verify Context7 installation")
        sys.exit(1)

    print()

    # Step 3: Setup .claude directory
    print("Step 3: Setting up .claude directory...")
    setup_claude_directory()

    print()

    # Step 4: Test MCP server
    print("Step 4: Testing MCP server...")
    test_mcp_server()

    print()

    # Print summary
    print_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)
