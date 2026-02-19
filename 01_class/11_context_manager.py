import time
import asyncio
from contextlib import contextmanager, asynccontextmanager

@contextmanager
def sync_context():
    print("[SYNC] Enter")
    start = time.time()
    try:
        yield "SYNC RESOURCE"
    finally:
        end = time.time()
        print(f"[SYNC] Exit (elapsed: {end - start:.2f}s)")

@asynccontextmanager
async def async_context():
    print("[ASYNC] Enter")
    start = time.time()
    try:
        yield "ASYNC RESOURCE"
    finally:
        end = time.time()
        print(f"[ASYNC] Exit (elapsed: {end - start:.2f}s)")

def run_sync():
    print("\n=== Running Sync Context ===")
    with sync_context() as resource:
        print(f"Using: {resource}")
        time.sleep(1)


async def run_async():
    print("\n=== Running Async Context ===")
    async with async_context() as resource:
        print(f"Using: {resource}")
        await asyncio.sleep(1)


if __name__ == "__main__":
    run_sync()
    asyncio.run(run_async())
