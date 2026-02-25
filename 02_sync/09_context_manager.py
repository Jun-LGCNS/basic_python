class MyResource:
    def __enter__(self):
        print("리소스 획득")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("리소스 해제")



import asyncio

class AsyncResource:
    async def __aenter__(self):
        print("비동기 리소스 획득 시작")
        await asyncio.sleep(1)
        print("비동기 리소스 획득 완료")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("비동기 리소스 해제 시작")
        await asyncio.sleep(1)
        print("비동기 리소스 해제 완료")

async def main():
    async with AsyncResource() as r:
        print("비동기 작업 수행")


# 현업에서 많이 쓰니까 익숙해지도록,,,

from contextlib import contextmanager, asynccontextmanager

@contextmanager
def my_resource():
    print("contextmanager 리소스 획득")
    try:
        yield "리소스 객체"
    finally:
        print("contextmanager 리소스 해제")

@asynccontextmanager
async def async_my_resource():
    print("asynccontextmanager 리소스 획득 시작")
    await asyncio.sleep(1)
    print("asynccontextmanager 리소스 획득 완료")

    try:
        yield "비동기 리소스 객체"
    finally:
        print("asynccontextmanager 리소스 해제 시작")
        await asyncio.sleep(1)
        print("asynccontextmanager 리소스 해제 완료")

async def async_main():
    async with async_my_resource() as r:
        print("비동기 작업 수행:", r)

if __name__ == "__main__":

    # 1. 동기 컨텍스트 매니저 사용
    with MyResource() as r:
        print("작업 수행")

    # 2. contextlib의 contextmanager 사용
    with my_resource() as r:
        print("작업 수행:", r)

    # 3. 비동기 컨텍스트 매니저 사용
    # asyncio.run(main())

    # 4. contextlib의 asynccontextmanager 사용
    # asyncio.run(async_main())



