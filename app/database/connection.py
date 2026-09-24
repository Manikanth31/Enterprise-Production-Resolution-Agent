import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "enterprise.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
SEED_PATH = PROJECT_ROOT / "database" / "seed_data.sql"


def initialize_database() -> Path:
    """Create the SQLite database and seed any missing demo records safely."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    try:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()

        if not tables and SCHEMA_PATH.exists():
            connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        if SEED_PATH.exists():
            connection.executescript(SEED_PATH.read_text(encoding="utf-8"))
    finally:
        connection.close()

    return DATABASE_PATH


def get_connection():
    """Create a connection to the enterprise SQLite database."""
    initialize_database()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection