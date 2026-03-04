"""
02_sqlite_connect.py
주제:
- sqlite3 연결
- cursor/execute/commit/close
"""

import sqlite3

DB_PATH = "crud_demo.db"


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT sqlite_version();")
    version = cursor.fetchone()
    print("SQLite version:", version[0])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
