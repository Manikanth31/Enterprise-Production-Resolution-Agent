import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/enterprise.db")


def get_connection():
    """Create a connection to the enterprise SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection