"""
09_decorator.py
주제:
- 데코레이터 기본 구조
- 함수 감싸기
- 인자 전달
- 반환값 유지
"""

import time


def logging_decorator(func):
    """
    TODO:
    1. 함수 실행 전에 "[LOG] 함수 시작" 출력
    2. 함수 실행 후 "[LOG] 함수 종료" 출력
    3. 원래 함수의 반환값을 그대로 반환하도록 수정하세요.
    """

    def wrapper():
        print("[LOG] 함수 시작")
        func()
        print("[LOG] 함수 종료")
        # 현재는 반환값을 돌려주지 않음 (일부러 틀림)

    return wrapper


@logging_decorator
def say_hello():
    print("안녕하세요!")
    return "HELLO"


# ------------------------------
# 심화: 인자가 있는 함수
# ------------------------------

def timer_decorator(func):
    """
    TODO:
    - 실행 시간을 측정하도록 완성하세요.
    - *args, **kwargs를 사용해야 합니다.
    """

    def wrapper(a, b):
        start = time.time()
        result = func(a, b)  # 현재는 인자를 못 받음 (일부러 틀림)
        end = time.time()
        print(f"실행 시간: {end - start:.6f}초")
        return result

    return wrapper


@timer_decorator
def slow_add(a, b):
    time.sleep(1)
    return a + b


if __name__ == "__main__":
    print("---- say_hello ----")
    result = say_hello()
    print("반환값:", result)

    print("\n---- slow_add ----")
    print(slow_add(3, 4))  # 현재는 에러 발생해야 정상