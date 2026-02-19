"""
06_magic_call.py
주제:
- __call__
- 객체를 함수처럼 사용
"""

class Multiplier:

    def __init__(self, number):
        self.number = number

    def __call__(self, value):
        """
        TODO:
        value * self.number 를 반환하도록 수정하세요.
        """
        return value * self.number  # 일부러 틀림


if __name__ == "__main__":
    m = Multiplier(10)
    print(m(5))  # 50이 나오도록 수정