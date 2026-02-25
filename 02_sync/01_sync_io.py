import time

def download(file_name):
    print(f"{file_name} 다운로드 시작")
    time.sleep(2)
    print(f"{file_name} 다운로드 완료")

start = time.time()

download("A")
download("B")
download("C")

end = time.time()
print("총 소요 시간:", end - start)