"""
04_select_basic.py
주제:
- SELECT
- WHERE / ORDER BY / LIMIT
"""

import sqlite3

DB_PATH = "crud_demo.db"


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("[전체 조회]")
    cursor.execute("SELECT id, name, team, age FROM employees;")
    for row in cursor.fetchall():
        print(row)

    print("\n[조건 조회: team='AI']")
    cursor.execute(
        "SELECT id, name, team, age FROM employees WHERE team = ? ORDER BY age DESC LIMIT 5;",
        ("AI",),
    )
    for row in cursor.fetchall():
        print(row)

    conn.close()



if __name__ == "__main__":
    main()
