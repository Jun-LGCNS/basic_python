# 01_iterator_basic.py

numbers = [1, 2, 3]

# 1. 리스트는 iterable 객체
iterator = iter(numbers)

print(next(iterator))  # 1
print(next(iterator))  # 2
print(next(iterator))  # 3
print(next(iterator))  # StopIteration 발생