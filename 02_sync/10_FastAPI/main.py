from fastapi import FastAPI
import time
import asyncio

app = FastAPI()

@app.get("/chat")
async def chat():
    print("요청 시작")
    # time.sleep(2)   # ❌ 이벤트 루프 블로킹
    await asyncio.sleep(2)  # ✅ 이벤트 루프 비블로킹
    print("요청 종료")
    return {"message": "응답 완료"}

# 켜는법 : python -m uvicorn 02_sync.10_FastAPI.main:app --reload