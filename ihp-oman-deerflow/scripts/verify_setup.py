#!/usr/bin/env python3
"""
IHP Oman DeerFlow - Setup Verification Script
Verifies all Phase 1 setup components are working
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def check_directories():
    """Check all required directories exist."""
    print("\n[1/5] Checking directory structure...")
    required_dirs = [
        ".deer-flow",
        ".deer-flow/logs",
        ".deer-flow/agent_outputs",
        "database",
        "scripts",
        "agents",
        "skills/public",
        "integrations",
        "tests",
    ]

    all_good = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (missing)")
            all_good = False

    return all_good


def check_files():
    """Check all required files exist."""
    print("\n[2/5] Checking configuration files...")
    required_files = [
        "config/config.yaml",
        "config/extensions_config.json",
        "config/.env.example",
        "database/schema.sql",
        "requirements.txt",
        ".env",
    ]

    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (missing)")
            all_good = False

    return all_good


def check_database():
    """Check database is initialized."""
    print("\n[3/5] Checking database...")
    db_path = os.getenv("DATABASE_URL", ".deer-flow/ihp_oman.db").replace("sqlite:///", "")

    if not Path(db_path).exists():
        print(f"  ✗ Database not found: {db_path}")
        return False

    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = [
            'rfq_tracking', 'quotation_tracking', 'po_tracking',
            'vdp_tracking', 'compliance_tracking', 'collections_tracking',
            'payables_tracking', 'agent_logs', 'alerts'
        ]

        missing_tables = [t for t in required_tables if t not in tables]
        if missing_tables:
            print(f"  ✗ Missing tables: {', '.join(missing_tables)}")
            conn.close()
            return False

        # Check VDP data
        cursor.execute("SELECT COUNT(*) FROM vdp_tracking")
        vdp_count = cursor.fetchone()[0]

        if vdp_count == 0:
            print(f"  ✗ No VDP baseline data found")
            conn.close()
            return False

        print(f"  ✓ Database initialized ({len(tables)} tables, {vdp_count} operators)")
        conn.close()
        return True

    except Exception as e:
        print(f"  ✗ Database check failed: {e}")
        return False


def check_environment_variables():
    """Check critical environment variables are set."""
    print("\n[4/5] Checking environment variables...")

    critical_vars = [
        "ANTHROPIC_API_KEY",
        "DEERFLOW_PORT",
        "DATABASE_URL",
    ]

    optional_vars = [
        "OPENAI_API_KEY",
        "TAVILY_API_KEY",
        "PDO_USERNAME",
        "TATWEER_EMAIL",
        "OUTLOOK_EMAIL",
        "LANGSMITH_API_KEY",
    ]

    all_good = True
    for var in critical_vars:
        value = os.getenv(var)
        if value and len(value) > 5:
            print(f"  ✓ {var} (configured)")
        else:
            print(f"  ✗ {var} (NOT SET - required)")
            all_good = False

    print("\n  Optional environment variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value and len(value) > 5:
            print(f"  ✓ {var} (configured)")
        else:
            print(f"  ○ {var} (optional, can be configured later)")

    return all_good


def check_python_modules():
    """Check critical Python modules can be imported."""
    print("\n[5/5] Checking Python dependencies...")

    critical_modules = [
        "dotenv",
        "pydantic",
        "yaml",
    ]

    optional_modules = [
        "anthropic",
        "langchain",
        "deerflow",
        "fastapi",
        "sqlalchemy",
    ]

    all_good = True
    for module in critical_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} (NOT INSTALLED - required)")
            all_good = False

    print("\n  Optional modules:")
    for module in optional_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ○ {module} (optional, install with: pip install {module})")

    return all_good


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("IHP Oman DeerFlow - Setup Verification")
    print("=" * 70)

    checks = [
        ("Directory Structure", check_directories),
        ("Configuration Files", check_files),
        ("Database Initialization", check_database),
        ("Environment Variables", check_environment_variables),
        ("Python Dependencies", check_python_modules),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error during {name}: {e}")
            results.append((name, False))

    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)

    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n✓ Phase 1 Setup Verification PASSED")
        print("\nReady for Phase 2: Agent Deployment")
        return 0
    else:
        print("\n✗ Phase 1 Setup Verification FAILED")
        print("\nPlease fix the issues above before proceeding to Phase 2")
        return 1


if __name__ == "__main__":
    sys.exit(main())
