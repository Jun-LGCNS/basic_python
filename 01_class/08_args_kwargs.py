"""
08_args_kwargs.py
주제:
- *args
- **kwargs
- 인자 패킹 & 언패킹
"""


def add_all(*args):
    """
    TODO:
    - 모든 숫자를 더해서 반환하도록 수정하세요.
    - args는 튜플이라는 것을 확인해보세요.
    """
    print("args:", args)
    return sum(args)  # 일부러 틀림


def print_user(**kwargs):
    """
    TODO:
    - kwargs는 딕셔너리입니다.
    - key와 value를 출력하도록 수정하세요.
    """
    print("kwargs_keys:", list(kwargs.keys()))
    print("kwargs_values:", list(kwargs.values()))


# ---------------------------------
# 심화: args + kwargs 같이 사용
# ---------------------------------

def example_function(a, b, *args, **kwargs):
    """
    TODO:
    출력 형식 예시:

    a: 1
    b: 2
    args: (3, 4)
    kwargs: {'x': 10, 'y': 20}
    """
    print(f"a : {a}")
    print(f"b : {b}")
    print(f"args : {args}")
    print(f"kwargs : {kwargs}")
    pass


if __name__ == "__main__":

    print("---- add_all ----")
    print(add_all(1, 2, 3, 4))

    print("\n---- print_user ----")
    print_user(name="홍길동", age=28, team="AI")

    print("\n---- example_function ----")
    example_function(1, 2, 3, 4, x=10, y=20)