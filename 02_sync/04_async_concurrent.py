import asyncio
import time

async def download(file_name):
    print(f"{file_name} 시작")
    await asyncio.sleep(2) # time.sleep(2)로 변경하세요
    print(f"{file_name} 완료")

async def main():
    await asyncio.gather(
        download("A"),
        download("B")
    )

start = time.time()
asyncio.run(main())
print("총 시간:", time.time() - start)
