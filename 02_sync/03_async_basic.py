import asyncio
import time

async def download(file_name):
    print(f"{file_name} 시작")
    await asyncio.sleep(2)
    print(f"{file_name} 완료")

async def main():
    start_time = time.time()
    await asyncio.gather(download("A"), download("B"))
    print("총 소요 시간:", time.time() - start_time)

asyncio.run(main())