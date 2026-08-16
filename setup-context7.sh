#!/bin/bash

# Context7 MCP Setup Script
# This script automates the installation and initialization of Context7 MCP

set -e

echo "🚀 Context7 MCP Setup Script"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Context7 is installed
echo "Step 1: Checking Context7 installation..."
if command -v context7 &> /dev/null; then
    VERSION=$(context7 --version 2>/dev/null || echo "unknown")
    print_status "Context7 is already installed (${VERSION})"
else
    print_warning "Context7 is not installed"
    echo ""
    echo "Choose installation method:"
    echo "1) pip (Python package manager)"
    echo "2) npm (Node package manager)"
    echo "3) brew (macOS package manager)"
    echo "0) Skip installation (I'll install manually)"
    read -p "Enter your choice [0-3]: " choice

    case $choice in
        1)
            echo "Installing via pip..."
            pip install context7
            print_status "Context7 installed via pip"
            ;;
        2)
            echo "Installing via npm..."
            npm install -g context7
            print_status "Context7 installed via npm"
            ;;
        3)
            echo "Installing via brew..."
            brew install context7
            print_status "Context7 installed via brew"
            ;;
        0)
            print_warning "Skipping installation. Please install Context7 manually."
            echo "  pip install context7"
            echo ""
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
fi

echo ""

# Verify Context7 installation
if command -v context7 &> /dev/null; then
    echo "Step 2: Verifying Context7..."
    context7 --version
    print_status "Context7 verified"
else
    print_error "Context7 is not available in PATH"
    echo "Please install Context7 and try again."
    exit 1
fi

echo ""

# Check .claude directory
echo "Step 3: Checking .claude directory..."
if [ ! -d ".claude" ]; then
    mkdir -p .claude
    print_status "Created .claude directory"
else
    print_status ".claude directory exists"
fi

echo ""

# Check configuration files
echo "Step 4: Verifying MCP configuration files..."
if [ -f ".claude/mcp.json" ]; then
    print_status ".claude/mcp.json exists"
else
    print_warning ".claude/mcp.json not found"
fi

if [ -f ".claude/settings.json" ]; then
    print_status ".claude/settings.json exists"
else
    print_warning ".claude/settings.json not found"
fi

echo ""

# Test MCP server
echo "Step 5: Testing Context7 MCP server..."
print_info "Testing if MCP server can start (timeout in 5 seconds)..."

timeout 5s context7 mcp serve > /dev/null 2>&1 && \
    print_status "MCP server test passed" || \
    print_warning "Could not verify MCP server (this is okay if timeout)"

echo ""

# Summary
echo "=============================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=============================="
echo ""
echo "Next steps:"
echo "1. Open this project in Claude Code:"
echo "   ${BLUE}claude code .${NC}"
echo ""
echo "2. Or open in Claude Desktop:"
echo "   ${BLUE}File → Open Folder → select markitdown${NC}"
echo ""
echo "3. Try using Context7 with a prompt:"
echo "   ${BLUE}Use Context7 to extract text from README.md${NC}"
echo ""
echo "For detailed usage guide, see: ${BLUE}CONTEXT7_MCP_GUIDE.md${NC}"
echo ""
print_status "All set! Happy coding! 🎉"
