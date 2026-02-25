import time
import threading
from multiprocessing import Process

def cpu_task():
    count = 0
    for _ in range(50_000_000):
        count += 1


if __name__ == "__main__":
    # Thread 버전
    start = time.time()

    t1 = threading.Thread(target=cpu_task)
    t2 = threading.Thread(target=cpu_task)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print("Thread 시간:", time.time() - start)

    # Process 버전
    start = time.time()

    p1 = Process(target=cpu_task)
    p2 = Process(target=cpu_task)

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print("Process 시간:", time.time() - start)
