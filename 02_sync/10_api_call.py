import requests
import threading
import time

def fetch(url, thread_name):
    print(f"{thread_name} - 요청 시작")
    response = requests.get(url, verify=False) # verify=False는 SSL 인증서 검증을 비활성화합니다. 
    print(f"{thread_name} - 응답 길이:", len(response.text))
    return response.text

if __name__ == "__main__":
    start = time.time()
    url = "http://127.0.0.1:8000/chat"

    t1 = threading.Thread(target=fetch, args=(url, "Thread-1"))
    t2 = threading.Thread(target=fetch, args=(url, "Thread-2"))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("총 시간:", time.time() - start)

