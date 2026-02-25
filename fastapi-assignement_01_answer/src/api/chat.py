"""채팅 API 라우터.

이 파일의 목적:
- `/api/v1/chat` HTTP 엔드포인트를 제공합니다.

포함 내용:
- POST `/api/v1/chat` 라우트

사용 시점:
- 클라이언트가 채팅 요청을 보낼 때 사용합니다.
"""

from fastapi import APIRouter

from src.models.chat import ChatRequest, ChatResponse
from src.services.chat_service import generate_chat_response

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def create_chat(request: ChatRequest) -> ChatResponse:
    """채팅 요청을 받아 응답 메시지를 반환합니다."""
    # Step 1. Pydantic 모델로 요청 바디를 자동 검증합니다.
    # Step 2. 서비스 레이어로 비즈니스 로직을 위임합니다.
    return generate_chat_response(request)
