"""
04_staticmethod.py
주제:
- staticmethod
- 인스턴스/클래스와 무관한 유틸 함수
"""

class Validator:

    @staticmethod
    def is_email(value):
        """
        TODO:
        - 문자열인지 확인
        - '@'가 포함되어 있는지 확인
        - 간단한 이메일 형식 검증 구현
        """
        if ("@" in value) and isinstance(value, str):
            return True
        else:
            return False # 일부러 틀림


if __name__ == "__main__":
    print(Validator.is_email("test@test.com"))
    print(Validator.is_email("invalid-email"))