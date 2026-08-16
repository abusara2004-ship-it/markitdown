# Context7 MCP Setup & Usage Guide

This guide walks you through initializing and using the Context7 MCP server with the MarkItDown project.

## 📋 Table of Contents
1. [Installation](#installation)
2. [Initialization](#initialization)
3. [Configuration](#configuration)
4. [Usage Examples](#usage-examples)
5. [Troubleshooting](#troubleshooting)

---

## Installation

### Step 1: Install Context7

#### Option A: Using pip (Python)
```bash
pip install context7
```

#### Option B: Using npm (Node.js)
```bash
npm install -g context7
```

#### Option C: Using brew (macOS)
```bash
brew install context7
```

### Step 2: Verify Installation
```bash
# Check if Context7 is installed
context7 --version

# Should output something like:
# Context7 version X.X.X

# Check if it's in your PATH
which context7
```

### Step 3: Verify MCP Command
```bash
# Test if the MCP serve command is available
context7 mcp --help

# Or test starting the MCP server (Ctrl+C to stop)
context7 mcp serve
```

---

## Initialization

### Method 1: Initialize in Claude Code (Recommended)

#### Step 1: Open Project
```bash
# Navigate to markitdown project
cd /path/to/markitdown

# Open in Claude Code
claude code .
```

#### Step 2: Verify Configuration Files
The MCP configuration should already be in place:
```
.claude/
├── mcp.json          # MCP server configuration
└── settings.json     # Project settings
```

#### Step 3: Initialize the MCP Server
In Claude Code, the MCP server initializes automatically on startup. You'll see:
- ✅ MCP Server connecting...
- ✅ Context7 MCP loaded
- ✅ Tools available

### Method 2: Manual Initialization

#### Step 1: Start the MCP Server Manually
```bash
# Terminal 1: Start Context7 MCP server
context7 mcp serve

# You should see output like:
# MCP Server started on stdio
# Ready to accept messages
```

#### Step 2: Connect Claude Code
```bash
# Terminal 2: Open Claude Code
cd /path/to/markitdown
claude code .
```

#### Step 3: Verify Connection
- Claude Code should automatically detect the MCP server
- You'll see "Context7" listed as an available tool

### Method 3: Initialize with MCP Inspector (Debugging)

```bash
# Terminal 1: Start MCP Inspector
npx @modelcontextprotocol/inspector

# Terminal 2: Open Inspector in browser
# Navigate to: http://localhost:5173

# In Inspector:
# 1. Select Transport Type: STDIO
# 2. Command: context7
# 3. Args: ["mcp", "serve"]
# 4. Click "Connect"
# 5. Go to "Tools" tab → "List Tools"
```

---

## Configuration

### Configuration Files

#### `.claude/mcp.json`
Defines how the MCP server should start:

```json
{
  "mcpServers": {
    "context7": {
      "command": "context7",
      "args": ["mcp", "serve"],
      "env": {
        "CONTEXT7_DEBUG": "false"
      }
    }
  }
}
```

**Available environment variables:**
- `CONTEXT7_DEBUG`: Enable debug logging (true/false)
- `CONTEXT7_TIMEOUT`: Request timeout in seconds (default: 30)
- `CONTEXT7_LOG_LEVEL`: Logging level (debug, info, warn, error)

#### `.claude/settings.json`
Project-level configuration:

```json
{
  "name": "markitdown",
  "description": "MarkItDown - Convert files to Markdown for LLMs",
  "mcpServers": ["context7"],
  "allowedTools": ["bash", "git"]
}
```

### Configuration for Claude Desktop

Edit your Claude Desktop config:

**macOS/Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Add this configuration:**
```json
{
  "mcpServers": {
    "context7": {
      "command": "context7",
      "args": ["mcp", "serve"],
      "env": {
        "CONTEXT7_DEBUG": "false"
      }
    }
  }
}
```

Then restart Claude Desktop.

---

## Usage Examples

### Example 1: Extract Text from File

**Prompt:**
```
Use Context7 to extract all text from the README.md file in this project
```

**Claude's response:**
```
I'll use Context7 to extract the text from README.md...
[Context7 processes the file]
Here's the extracted text:
# MarkItDown
[![PyPI]...
```

### Example 2: Convert File to Markdown

**Prompt:**
```
Can you use Context7 to convert packages/markitdown/tests/test_files/test.pdf to markdown?
```

**Claude's response:**
```
I'll convert that PDF to markdown using Context7...
[Context7 processes the PDF]
# Document Title
## Section 1
Content here...
```

### Example 3: Process Multiple Files

**Prompt:**
```
Use Context7 to extract text from all markdown files in the packages/ directory and give me a summary
```

**Claude's response:**
```
I'll use Context7 to process all markdown files...
[Context7 processes multiple files]
Summary:
- packages/markitdown-mcp/README.md: MCP server documentation
- packages/markitdown-ocr/README.md: OCR plugin information
...
```

### Example 4: Get File Metadata

**Prompt:**
```
Context7, what's the metadata of the main markitdown package?
```

**Claude's response:**
```
I'll retrieve the metadata using Context7...
[Context7 analyzes the package]
Package Information:
- Name: markitdown
- Version: 0.1.6
- Author: Adam Fourney
- License: MIT
```

### Example 5: Analyze Document Structure

**Prompt:**
```
Can Context7 analyze the structure of SECURITY.md and tell me what sections it contains?
```

**Claude's response:**
```
I'll analyze SECURITY.md using Context7...
[Context7 processes the file]
Document Structure:
1. Introduction
2. Security Considerations
3. Reporting Vulnerabilities
...
```

---

## Troubleshooting

### Issue 1: "Context7 command not found"

**Solution:**
```bash
# Reinstall Context7
pip install --upgrade context7

# Or verify PATH
echo $PATH

# Add to PATH if needed (macOS/Linux)
export PATH="$HOME/.local/bin:$PATH"
```

### Issue 2: "MCP Server failed to start"

**Solution:**
```bash
# Check if Context7 is working
context7 --version

# Try manual MCP start
context7 mcp serve

# Check for error messages
context7 mcp serve --debug
```

### Issue 3: "Tools not showing in Claude"

**Solution:**
```bash
# Restart Claude Code
# In terminal: Ctrl+C, then `claude code .` again

# Or restart Claude Desktop completely
# macOS: Quit Claude, reopen

# Verify .claude/mcp.json exists
ls -la .claude/mcp.json
```

### Issue 4: "Connection timeout"

**Solution:**
```bash
# Increase timeout in .claude/mcp.json
{
  "mcpServers": {
    "context7": {
      "command": "context7",
      "args": ["mcp", "serve"],
      "env": {
        "CONTEXT7_TIMEOUT": "60"
      }
    }
  }
}
```

### Issue 5: "Permission denied"

**Solution:**
```bash
# Make sure context7 is executable
chmod +x $(which context7)

# Or reinstall with proper permissions
pip install --user context7
```

---

## Quick Start Checklist

- [ ] Install Context7: `pip install context7`
- [ ] Verify installation: `context7 --version`
- [ ] Clone markitdown repo: `git clone <repo-url>`
- [ ] Navigate to project: `cd markitdown`
- [ ] Check `.claude/mcp.json` exists: `ls .claude/mcp.json`
- [ ] Open in Claude Code: `claude code .`
- [ ] Test with a prompt: "Use Context7 to extract text from README.md"
- [ ] Verify it works! ✅

---

## Advanced Usage

### Running with Debug Output

```bash
# Enable debug logging
export CONTEXT7_DEBUG=true
context7 mcp serve
```

### Custom Environment Variables

Edit `.claude/mcp.json`:
```json
{
  "mcpServers": {
    "context7": {
      "command": "context7",
      "args": ["mcp", "serve"],
      "env": {
        "CONTEXT7_DEBUG": "true",
        "CONTEXT7_LOG_LEVEL": "debug",
        "CONTEXT7_TIMEOUT": "60",
        "CUSTOM_VAR": "value"
      }
    }
  }
}
```

### Using with Docker

```bash
# Run Context7 in Docker
docker run -it context7:latest context7 mcp serve

# Mount local directory
docker run -it -v /path/to/markitdown:/workspace context7:latest \
  context7 mcp serve
```

---

## Support & Resources

- **Context7 Documentation**: https://context7.io/docs
- **MCP Protocol**: https://modelcontextprotocol.io
- **MarkItDown Repo**: https://github.com/microsoft/markitdown
- **Issues**: Report problems in the project's GitHub issues

---

## Next Steps

1. ✅ Follow the "Quick Start Checklist" above
2. 📚 Read through "Usage Examples"
3. 🔧 Try customizing the configuration
4. 💬 Start using Context7 with Claude!

Happy coding! 🚀
