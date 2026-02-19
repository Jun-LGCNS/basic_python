"""
03_classmethod.py
주제:
- classmethod
- 대체 생성자
"""

class User:

    default_role = "USER"

    def __init__(self, name, role=None):
        self.name = name
        self.role = role if role else self.default_role

    @classmethod
    def from_string(cls, text):
        """
        TODO:
        "이름,역할" 형식의 문자열을 받아서
        User 객체를 생성하도록 완성하세요.

        예:
        "홍길동,ADMIN"
        """
        cls.name, cls.role = text.split(",")
        return cls

    @classmethod
    def change_default_role(cls, new_role):
        cls.default_role = new_role


if __name__ == "__main__":
    User.change_default_role("GUEST")
    u = User("김철수")
    print(u.role)

    u2 = User.from_string("홍길동,ADMIN")
    print(u2.name, u2.role)