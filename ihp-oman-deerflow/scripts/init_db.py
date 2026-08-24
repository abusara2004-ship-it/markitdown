#!/usr/bin/env python3
"""
IHP Oman DeerFlow Database Initialization
Initializes SQLite database with schema and seed data
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta


def init_database(db_path: str):
    """Initialize the database with schema and seed data."""
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read and execute schema
    schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
    if schema_path.exists():
        with open(schema_path, 'r') as f:
            schema = f.read()
            cursor.executescript(schema)
        print(f"✓ Database schema initialized: {db_path}")
    else:
        print(f"✗ Schema file not found: {schema_path}")
        return False

    # Seed initial data for operators and VDP tracking
    try:
        # VDP baseline data
        operators = [
            ("Petroleum Development Oman", "106883", 68.96, 90.0, "critical"),
            ("OQ / OQ8", "OQ8", 75.0, 85.0, "high"),
            ("bp Oman", "BP-OM", 80.0, 85.0, "high"),
            ("Shell Oman", "SHELL-OM", 78.0, 85.0, "high"),
            ("Marsa LNG", "MARSA-LNG", 82.0, 85.0, "medium"),
            ("MEDCO LLC", "MEDCO", 85.0, 80.0, "medium"),
            ("Tatweer / Business Gateways", "TATWEER", 76.0, 80.0, "medium"),
        ]

        for op_name, op_code, vdp, threshold, priority in operators:
            cursor.execute(
                """INSERT OR IGNORE INTO vdp_tracking
                   (operator_name, operator_code, vdp_percentage, vdp_threshold,
                    vdp_status, last_calculated)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (op_name, op_code, vdp, threshold,
                 "critical" if vdp < threshold else "normal",
                 datetime.now().isoformat())
            )

        conn.commit()
        print(f"✓ Operator VDP baseline data seeded ({len(operators)} operators)")

    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        return False

    finally:
        conn.close()

    return True


def verify_database(db_path: str) -> bool:
    """Verify database is properly initialized."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check table existence
        tables = [
            'rfq_tracking', 'quotation_tracking', 'po_tracking',
            'vdp_tracking', 'compliance_tracking', 'collections_tracking',
            'payables_tracking', 'agent_logs', 'alerts'
        ]

        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cursor.fetchone():
                print(f"✗ Missing table: {table}")
                return False

        # Check VDP data
        cursor.execute("SELECT COUNT(*) FROM vdp_tracking")
        count = cursor.fetchone()[0]
        if count == 0:
            print("✗ No VDP baseline data found")
            return False

        conn.close()
        print(f"✓ Database verification passed ({len(tables)} tables, {count} operators)")
        return True

    except Exception as e:
        print(f"✗ Database verification failed: {e}")
        return False


if __name__ == "__main__":
    # Get database path from environment or default
    db_path = os.getenv("DATABASE_URL", ".deer-flow/ihp_oman.db")

    print("=" * 70)
    print("IHP Oman DeerFlow - Database Initialization")
    print("=" * 70)

    if init_database(db_path):
        if verify_database(db_path):
            print("\n✓ Database initialization complete and verified")
            exit(0)
        else:
            print("\n✗ Database initialization completed but verification failed")
            exit(1)
    else:
        print("\n✗ Database initialization failed")
        exit(1)
