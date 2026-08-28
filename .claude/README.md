# Claude Code Configuration

This directory contains configuration files for Claude Code and Claude Desktop integration with the MarkItDown project.

## Files

### `mcp.json`
Configures the Model Context Protocol (MCP) servers available to Claude.

**Current MCP Servers:**
- **context7**: A Context Management and Development Protocol server for advanced code context handling

### `settings.json`
Project-specific settings for Claude Code and Claude Desktop.

**Configuration:**
- Project name and description
- Enabled MCP servers
- Allowed tools and operations

## Context7 MCP

The Context7 MCP server is automatically initialized when you open this project in Claude Code or Claude Desktop.

### Quick Start

1. **Open project in Claude Code:**
   ```bash
   claude code .
   ```

2. **Or open in Claude Desktop:**
   - Click File → Open Folder
   - Select the markitdown directory

3. **Start using Context7:**
   - Ask Claude to use Context7 in your prompts
   - Example: "Use Context7 to extract text from README.md"

### Setup & Configuration

For detailed setup instructions, see:
- `CONTEXT7_MCP_GUIDE.md` - Comprehensive usage guide
- `setup-context7.sh` - Automated setup (macOS/Linux)
- `setup-context7.bat` - Automated setup (Windows)
- `setup_context7.py` - Python setup script (cross-platform)

### Environment Variables

You can customize Context7 behavior by adding environment variables to `mcp.json`:

```json
{
  "mcpServers": {
    "context7": {
      "command": "context7",
      "args": ["mcp", "serve"],
      "env": {
        "CONTEXT7_DEBUG": "false",
        "CONTEXT7_TIMEOUT": "30",
        "CONTEXT7_LOG_LEVEL": "info"
      }
    }
  }
}
```

### Troubleshooting

**MCP not loading?**
- Ensure Context7 is installed: `pip install context7`
- Restart Claude Code or Claude Desktop
- Check that `.claude/mcp.json` exists and is valid JSON

**Tools not appearing?**
- Verify Context7 is in your PATH: `which context7`
- Use MCP Inspector to debug: `npx @modelcontextprotocol/inspector`

**Still having issues?**
- See the full troubleshooting guide in `CONTEXT7_MCP_GUIDE.md`
- Check Context7 logs: `CONTEXT7_DEBUG=true context7 mcp serve`

## Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Claude Code Guide](https://code.claude.com/)
- [MarkItDown Repository](https://github.com/microsoft/markitdown)

## Next Steps

1. Run the setup script:
   - **Linux/macOS:** `./setup-context7.sh`
   - **Windows:** `setup-context7.bat`
   - **Python (cross-platform):** `python setup_context7.py`

2. Read the comprehensive guide: `CONTEXT7_MCP_GUIDE.md`

3. Start using Context7 with Claude!

---

*For questions or issues, refer to the main project's README.md and contributing guidelines.*
