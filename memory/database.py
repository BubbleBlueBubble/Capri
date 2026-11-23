from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "capricorn.db"


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


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
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """)
        connection.commit()
    finally:
        connection.close()


def save_message(role, content):
    connection = connect()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO messages (role, content)
            VALUES (?, ?)
            """,
            (role, content),
        )
        connection.commit()
    finally:
        connection.close()


def get_last_messages(limit=10):
    connection = connect()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT role, content FROM (
                SELECT id, role, content
                FROM messages
                ORDER BY id DESC
                LIMIT ?
            )
            ORDER BY id ASC
            """,
            (limit,),
        )
        rows = cursor.fetchall()

        return [
            {"role": row["role"], "content": row["content"]}
            for row in rows
        ]
    finally:
        connection.close()


def clear_messages():
    connection = connect()

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM messages")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'messages'")
        connection.commit()
    finally:
        connection.close()


def save_fact(category, key, value):
    connection = connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO facts (category, key, value)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                category = excluded.category,
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (category.strip().lower(), key.strip().lower(), value.strip()),
        )
        connection.commit()
    finally:
        connection.close()


def get_all_facts():
    connection = connect()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT category, key, value 
            FROM facts
            ORDER BY category ASC, key ASC
            """)
        facts = cursor.fetchall()

        return [{"category": row["category"], "key": row["key"], "value": row["value"]} for row in facts]
    finally:
        connection.close()


def delete_fact(key):
    connection = connect()
    key = key.strip().lower()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM facts WHERE key = ?",
        (key,))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()

if __name__ == "__main__":
    init_db()
    delete_fact("name")
    save_fact("profile", "name", "KiriKiri")