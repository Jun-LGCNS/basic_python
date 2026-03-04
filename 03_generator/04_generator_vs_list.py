# 04_generator_vs_list.py

import sys

# 리스트
numbers_list = [i for i in range(1000000)]

# 제너레이터
numbers_gen = (i for i in range(1000000))

print(sys.getsizeof(numbers_list))
print(sys.getsizeof(numbers_gen))

# Keyword : Lazy Evaluation

