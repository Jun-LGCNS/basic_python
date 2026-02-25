import threading
import time

def task(name):
    print(f"{name} 시작")
    time.sleep(2)
    print(f"{name} 완료")

start = time.time()

t1 = threading.Thread(target=task, args=("A",))
t2 = threading.Thread(target=task, args=("B",)) # daemon은 메인 스레드가 끝나면 같이 끝나는 스레드 (join 안 해주면 바로 종료)
t1.start()
t2.start()

t1.join() # thread가 끝나고 다음으로 넘어가라
t2.join()

print("총 시간:", time.time() - start)