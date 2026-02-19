"""
05_abstract_method.py
주제:
- ABC
- abstractmethod
- 인터페이스 개념
"""

from abc import ABC, abstractmethod


class Animal(ABC):

    @abstractmethod
    def speak(self):
        pass


class Dog(Animal):
    """
    TODO:
    speak 메소드를 구현하세요.
    "멍멍"을 출력하도록 하세요.
    """
    def speak(self):
        print("멍멍")


class Cat(Animal):
    """
    TODO:
    speak 메소드를 구현하세요.
    "야옹"을 출력하도록 하세요.
    """
    def speak(self):
        print("야옹")


if __name__ == "__main__":
    d = Dog()
    d.speak()

    c = Cat()
    c.speak()