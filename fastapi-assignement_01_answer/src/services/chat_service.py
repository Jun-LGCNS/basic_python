"""채팅 도메인 서비스.

이 파일의 목적:
- 라우터에서 분리된 채팅 응답 생성 로직을 제공합니다.

포함 내용:
- generate_chat_response 함수

사용 시점:
- HTTP 처리와 비즈니스 로직을 분리하고 싶을 때 사용합니다.
"""

from src.models.chat import ChatRequest, ChatResponse


def generate_chat_response(request: ChatRequest) -> ChatResponse:
    """요청 정보를 바탕으로 고정 메시지 응답을 생성합니다."""
    # Step 3. 현재 튜토리얼 단계에서는 streaming 여부와 무관하게 동일한 응답을 반환합니다.
    _ = request

    return ChatResponse(message="답변이 생성되었습니다.")
