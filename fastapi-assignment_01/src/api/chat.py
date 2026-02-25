from fastapi import APIRouter

"""채팅 API 라우터.

이 파일의 목적:
- `/api/v1/chat` 엔드포인트 라우팅을 제공합니다.

포함 내용:
- POST `/api/v1/chat` 라우트 자리

사용 시점:
- 실습에서 FastAPI 라우터를 직접 구현할 때 사용합니다.
"""
from src.services.chat_service import generate_chat_response
from src.models.chat import ChatRequest, ChatResponse

router = APIRouter()

router.add_api_route(
    "/api/v1/chat",
    generate_chat_response,
    methods=["POST"]
)

