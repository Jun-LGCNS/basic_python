"""
05_update_delete.py
주제:
- UPDATE
- DELETE
- rowcount 확인
"""

import sqlite3

DB_PATH = "crud_demo.db"


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE employees SET team = ? WHERE name = ?;",
        ("Platform", "Kim"),
    )
    print("UPDATE rowcount:", cursor.rowcount)

    cursor.execute("DELETE FROM employees WHERE name = ?;", ("Lee",))
    print("DELETE rowcount:", cursor.rowcount)

    conn.commit()

    cursor.execute("SELECT id, name, team, age FROM employees;")
    print("[최종 데이터]")
    for row in cursor.fetchall():
        print(row)

    conn.close()


if __name__ == "__main__":
    main()
