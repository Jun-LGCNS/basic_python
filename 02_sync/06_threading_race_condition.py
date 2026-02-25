import threading
import time

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        with lock:  # 잠금 없이 실행하면 경쟁 상태 발생
            temp = counter
            time.sleep(0)   # 일부러 스레드 전환
            counter = temp + 1

threads = [threading.Thread(target=increment) for _ in range(5)] # 리스트 컴프리헨션

for t in threads:
    t.start()
for t in threads:
    t.join()

print("결과:", counter)

# R_Lock, condition도 알아보기