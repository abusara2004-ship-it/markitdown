# Context7 MCP - Quick Start Guide

## 🚀 30-Second Setup

### Option 1: Automatic Setup (Recommended)

**On Linux/macOS:**
```bash
./setup-context7.sh
```

**On Windows:**
```bash
setup-context7.bat
```

**Cross-Platform (Python):**
```bash
python setup_context7.py
```

### Option 2: Manual Setup

```bash
# 1. Install Context7
pip install context7

# 2. Verify installation
context7 --version

# 3. Open in Claude Code
claude code .

# 4. Start using it!
```

---

## 💬 Common Usage Patterns

### Extract Text from Files
```
"Use Context7 to extract all text from README.md"
```

### Convert Files
```
"Convert packages/markitdown-mcp/README.md to markdown using Context7"
```

### Analyze Document Structure
```
"What sections does SECURITY.md contain? Use Context7 to analyze it"
```

### Get File Metadata
```
"Use Context7 to get metadata from the markitdown package"
```

### Process Multiple Files
```
"Extract text from all .md files in the packages directory using Context7"
```

---

## 📋 Files Overview

| File | Purpose |
|------|---------|
| `.claude/mcp.json` | MCP server configuration |
| `.claude/settings.json` | Project settings |
| `.claude/README.md` | Configuration guide |
| `CONTEXT7_MCP_GUIDE.md` | **Complete usage guide** |
| `setup-context7.sh` | Setup for Linux/macOS |
| `setup-context7.bat` | Setup for Windows |
| `setup_context7.py` | Setup for any OS |

---

## ✅ Verification Checklist

- [ ] Context7 installed: `context7 --version`
- [ ] MCP config exists: `ls .claude/mcp.json`
- [ ] Claude Code opened: `claude code .`
- [ ] Context7 visible in Claude
- [ ] Tried a test prompt

---

## 🐛 Troubleshooting

**"Command not found: context7"**
```bash
pip install context7
```

**"MCP not loading"**
- Restart Claude Code
- Check `.claude/mcp.json` syntax
- Verify Context7 is in PATH

**"Can't find tools"**
- Use MCP Inspector: `npx @modelcontextprotocol/inspector`
- Connect with STDIO transport
- Run "List Tools"

---

## 📚 Next Steps

1. ✅ Run setup script
2. 📖 Read: `CONTEXT7_MCP_GUIDE.md`
3. 💬 Start using Context7
4. 🔧 Customize if needed

---

## 🎯 Pro Tips

### Debug Mode
```bash
CONTEXT7_DEBUG=true context7 mcp serve
```

### Custom Timeout
Edit `.claude/mcp.json`:
```json
"env": {
  "CONTEXT7_TIMEOUT": "60"
}
```

### Running in Docker
```bash
docker run -it -v $(pwd):/workspace context7:latest
```

---

**Need more help?** See `CONTEXT7_MCP_GUIDE.md` for detailed documentation.

Happy coding! 🚀
