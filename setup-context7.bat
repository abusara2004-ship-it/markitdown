@echo off
REM Context7 MCP Setup Script for Windows
REM This script automates the installation and initialization of Context7 MCP

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Context7 MCP Setup Script (Windows)
echo ========================================
echo.

REM Check if Context7 is installed
echo Step 1: Checking Context7 installation...
where context7 >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Context7 is already installed
    context7 --version
) else (
    echo [WARNING] Context7 is not installed
    echo.
    echo Choose installation method:
    echo 1) pip (Python package manager - recommended)
    echo 2) npm (Node package manager)
    echo 0) Skip installation (I'll install manually)
    echo.
    set /p choice="Enter your choice [0-2]: "

    if "!choice!"=="1" (
        echo Installing via pip...
        pip install context7
        echo [OK] Context7 installed via pip
    ) else if "!choice!"=="2" (
        echo Installing via npm...
        npm install -g context7
        echo [OK] Context7 installed via npm
    ) else if "!choice!"=="0" (
        echo [WARNING] Skipping installation. Please install Context7 manually.
        echo   pip install context7
        echo.
    ) else (
        echo [ERROR] Invalid choice
        exit /b 1
    )
)

echo.

REM Verify Context7 installation
where context7 >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Context7 is not available in PATH
    echo Please install Context7 and try again.
    exit /b 1
)

echo Step 2: Verifying Context7...
context7 --version
echo [OK] Context7 verified

echo.

REM Check .claude directory
echo Step 3: Checking .claude directory...
if not exist ".claude" (
    mkdir .claude
    echo [OK] Created .claude directory
) else (
    echo [OK] .claude directory exists
)

echo.

REM Check configuration files
echo Step 4: Verifying MCP configuration files...
if exist ".claude\mcp.json" (
    echo [OK] .claude\mcp.json exists
) else (
    echo [WARNING] .claude\mcp.json not found
)

if exist ".claude\settings.json" (
    echo [OK] .claude\settings.json exists
) else (
    echo [WARNING] .claude\settings.json not found
)

echo.

REM Summary
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Open this project in Claude Code:
echo    claude code .
echo.
echo 2. Or open in Claude Desktop:
echo    File ^> Open Folder ^> select markitdown
echo.
echo 3. Try using Context7 with a prompt:
echo    Use Context7 to extract text from README.md
echo.
echo For detailed usage guide, see: CONTEXT7_MCP_GUIDE.md
echo.
echo [OK] All set! Happy coding! :)
echo.

pause
