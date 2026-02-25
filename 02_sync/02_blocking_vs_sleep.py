import requests
import time

def fetch(url):
    print("요청 시작")
    response = requests.get(url, verify=False)
    print("응답 길이:", len(response.text))

start = time.time()

fetch("https://httpbin.org/delay/2")
fetch("https://httpbin.org/delay/2")

print("총 시간:", time.time() - start)
