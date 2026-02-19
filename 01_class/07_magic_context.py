"""
07_magic_context.py
주제:
- with 문
- __enter__
- __exit__
"""

import time


class Timer:

    def __enter__(self):
        """
        TODO:
        시작 시간을 저장하세요.
        """
        self.time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        TODO:
        종료 시간을 구해서
        실행 시간을 출력하세요.
        """
        print(time.time() - self.time)


if __name__ == "__main__":
    with Timer():
        time.sleep(1)