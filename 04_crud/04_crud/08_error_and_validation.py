"""
08_error_and_validation.py
주제:
- 예외 처리
- 입력 검증
- UNIQUE 제약 조건
"""

import sqlite3

DB_PATH = "crud_demo.db"


def is_valid_name(name: str) -> bool:
    return bool(name and name.strip())


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL
        );
        """
    )
    conn.commit()

    email = "newhire@company.com"
    name = "New Hire"

    if not is_valid_name(name):
        print("이름 입력이 올바르지 않습니다.")
        conn.close()
        return

    try:
        cursor.execute(
            "INSERT INTO accounts (email, name) VALUES (?, ?);",
            (email, name),
        )
        conn.commit()
        print("첫 번째 INSERT 성공")

        cursor.execute(
            "INSERT INTO accounts (email, name) VALUES (?, ?);",
            (email, "Duplicate User"),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        print("중복/제약조건 오류:", e)
        conn.rollback()
    finally:
        rows = cursor.execute("SELECT id, email, name FROM accounts;").fetchall()
        print("\n[accounts]")
        for row in rows:
            print(row)
        conn.close()


if __name__ == "__main__":
    main()
