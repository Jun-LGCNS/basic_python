"""
06_transaction.py
주제:
- commit / rollback
- 트랜잭션 기본
"""

import sqlite3

DB_PATH = "crud_demo.db"


def print_employees(cursor: sqlite3.Cursor, title: str) -> None:
    print(f"\n[{title}]")
    cursor.execute("SELECT id, name, team, age FROM employees ORDER BY id;")
    for row in cursor.fetchall():
        print(row)


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 트랜잭션 격리 수준(Isolation Level) 4단계:
    # 1) Read Uncommitted: 커밋 전 데이터까지 읽을 수 있어 정합성 위험이 큼
    # 2) Read Committed: 커밋된 데이터만 읽음(더티 리드 방지)
    # 3) Repeatable Read: 같은 트랜잭션 내 재조회 결과를 보장
    # 4) Serializable: 트랜잭션을 순차 실행한 것처럼 동작(정합성 가장 강함)
    #
    # SQLite는 기본적으로 SERIALIZABLE에 가깝게 동작하며,
    # PRAGMA read_uncommitted = true 로 가장 낮은 수준에 가깝게 설정할 수 있음.

    print_employees(cursor, "시작 상태")

    try:
        cursor.execute(
            "INSERT INTO employees (name, team, age) VALUES (?, ?, ?);",
            ("Park", "Security", 27),
        )

        # 의도적 오류: 없는 컬럼에 INSERT
        cursor.execute(
            "INSERT INTO employees (name, team, no_column) VALUES (?, ?, ?);",
            ("Choi", "Infra", 29),
        )

        conn.commit()
    except Exception as e:
        print("\n오류 발생:", e)
        print("rollback 실행")
        conn.rollback()

    print_employees(cursor, "rollback 이후 상태")
    conn.close()


if __name__ == "__main__":
    main()
