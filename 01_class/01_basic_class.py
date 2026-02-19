"""
01_basic_class.py
주제:
- 클래스 기본 구조
- 인스턴스 메소드
- 클래스 변수
- __repr__
"""

class Employee:
    company = "LGCNS"  # 클래스 변수

    def __init__(self, name, age, team):
        self.name = name
        self.age = age
        self.team = team

    def introduce(self):
        """
        TODO:
        아래 형식으로 문자열을 반환하도록 수정하세요.

        예시:
        "안녕하세요. AI팀의 홍길동(28)입니다."
        """
        return f"안녕하세요 {self.team}팀의 {self.name}({self.age})입니다"

    def change_team(self, new_team):
        self.team = new_team

    def __repr__(self):
        """
        TODO:
        디버깅에 도움이 되는 형태로 수정하세요.

        예시:
        Employee(name='홍길동', age=28, team='AI')
        """
        return "Employee 객체"


emp = Employee("홍길동", 28, "AI")
print(emp)
print(emp.introduce())