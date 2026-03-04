"""
07_todo_crud_practice.py
주제:
- TODO 앱으로 CRUD 통합 실습
"""

import sqlite3

DB_PATH = "todo.db"


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    conn.commit()


def create_todo(conn: sqlite3.Connection, title: str) -> None:
    conn.execute("INSERT INTO todos (title) VALUES (?);", (title,))
    conn.commit()


def read_todos(conn: sqlite3.Connection) -> None:
    rows = conn.execute("SELECT id, title, done FROM todos ORDER BY id;").fetchall()
    print("\n[TODO 목록]")
    if not rows:
        print("데이터 없음")
    for todo_id, title, done in rows:
        status = "완료" if done else "진행중"
        print(f"{todo_id}. {title} [{status}]")


def update_todo_done(conn: sqlite3.Connection, todo_id: int, done: int) -> None:
    conn.execute("UPDATE todos SET done = ? WHERE id = ?;", (done, todo_id))
    conn.commit()


def delete_todo(conn: sqlite3.Connection, todo_id: int) -> None:
    conn.execute("DELETE FROM todos WHERE id = ?;", (todo_id,))
    conn.commit()


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    # 샘플 실행(입력 없이 바로 CRUD 흐름 확인)
    create_todo(conn, "SQL 기본 문법 익히기")
    create_todo(conn, "SELECT WHERE 연습")
    read_todos(conn)

    update_todo_done(conn, 1, 1)
    delete_todo(conn, 2)
    read_todos(conn)

    conn.close()


if __name__ == "__main__":
    main()
