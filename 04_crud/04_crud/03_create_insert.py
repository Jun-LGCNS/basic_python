"""
03_create_insert.py
주제:
- CREATE TABLE
- INSERT
"""

import sqlite3

DB_PATH = "crud_demo.db"


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            team TEXT NOT NULL,
            age INTEGER NOT NULL
        );
        """
    )

    cursor.execute(
        "INSERT INTO employees (name, team, age) VALUES (?, ?, ?);",
        ("Kim", "AI", 28),
    )
    cursor.execute(
        "INSERT INTO employees (name, team, age) VALUES (?, ?, ?);",
        ("Lee", "Data", 31),
    )

    conn.commit()
    conn.close()

    print("employees 테이블 생성 + 2건 INSERT 완료")


if __name__ == "__main__":
    main()
