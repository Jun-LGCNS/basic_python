"""
10_type_hint.py
주제:
- 기본 타입 힌트
- Optional
- list[int]
- dict[str, int]
- 반환 타입 명시
"""

from typing import Optional


def add(a : int, b : int) -> int:
    """
    TODO:
    타입 힌트를 추가하세요.
    a와 b는 int
    반환값도 int
    """
    return a + b


def greet(name : int, age : Optional[int]) -> str:
    """
    TODO:
    - name은 str
    - age는 Optional[int]
    - 반환값은 str
    """
    if age:
        return f"{name}({age})님 안녕하세요."
    return f"{name}님 안녕하세요."


def average(numbers : list[int]) -> float:
    """
    TODO:
    - numbers는 list[int]
    - 반환값은 float
    """
    return sum(numbers) / len(numbers)


def count_words(texts : list[str]) -> dict[str, int]:
    """
    TODO:
    - texts는 list[str]
    - 반환값은 dict[str, int]
    - 각 단어가 몇 번 등장하는지 세기
    """
    result = {}
    for text in texts:
        result[text] = result.get(text, 0) + 1
    return result


if __name__ == "__main__":
    print(add(1, 2))
    print(greet("홍길동", 28))
    print(average([1, 2, 3, 4]))
    print(count_words(["a", "b", "a"]))