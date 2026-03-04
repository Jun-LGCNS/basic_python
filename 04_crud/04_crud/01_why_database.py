"""
01_why_database.py
주제:
- 파일 저장과 데이터베이스 저장의 차이
- CRUD 개념 소개
"""

from pathlib import Path


def save_users_to_text(path: Path, users: list[dict]) -> None:
    """단순 파일 저장: 전체 내용을 다시 써야 해서 수정/삭제에 비효율적."""
    lines = [f"{u['id']},{u['name']},{u['team']}\n" for u in users]
    path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    users = [
        {"id": 1, "name": "Kim", "team": "AI"},
        {"id": 2, "name": "Lee", "team": "Data"},
    ]
    txt_path = Path("users.txt")

    save_users_to_text(txt_path, users)
    print("[파일 저장 결과]")
    print(txt_path.read_text(encoding="utf-8"))

    print("[CRUD 개념]")
    print("Create: 새로운 데이터 추가")
    print("Read: 저장된 데이터 조회")
    print("Update: 기존 데이터 수정")
    print("Delete: 기존 데이터 삭제")



if __name__ == "__main__":
    main()
