
from pathlib import Path
import sqlite3

# databese.py directory
BASE_DIR = Path(__file__).resolve().parent

# capricorn.db url
DB_PATH = BASE_DIR / "capricorn.db"

# db connection
def connect():
    return sqlite3.connect(DB_PATH)

# db creating
def init_db():
    connection = connect()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":
    init_db()
    connection = connect()

    ## db info
    # for column in connection.execute("PRAGMA table_info(messages)"):
    #     print(column)

    connection.close()