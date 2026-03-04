"""외부 LLM 게이트웨이 구현.

이 파일의 목적:
- 의도 분류와 최종 응답 생성을 BaseChatModel 기반으로 호출합니다.

포함 내용:
- LlmGateway 프로토콜
- HttpLlmGateway 구현

사용 시점:
- 채팅 완성 서비스에서 분류/생성 LLM 호출이 필요할 때 사용합니다.
"""

from collections.abc import Iterator
from typing import Literal, Protocol

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.services.langchain_chat_model import EndpointChatModel
from src.services.llm_parsing import parse_intent


class LlmGateway(Protocol):
    """LLM 호출 인터페이스."""

    def classify_intent(self, user_message: str) -> Literal["rag", "general"]:
        """사용자 메시지의 의도를 분류합니다."""

    def generate_text(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """최종 텍스트를 생성합니다."""

    def stream_text(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Iterator[str]:
        """최종 텍스트를 스트리밍으로 생성합니다."""


class HttpLlmGateway:
    """BaseChatModel을 사용해 외부 엔드포인트를 호출하는 게이트웨이."""

    def __init__(
        self,
        endpoint: str,
        model: str,
        default_temperature: float,
        default_max_tokens: int,
        timeout_seconds: float,
    ) -> None:
        self._default_temperature = default_temperature
        self._default_max_tokens = default_max_tokens
        self._chat_model = EndpointChatModel(
            endpoint=endpoint,
            model_name=model,
            request_timeout=timeout_seconds,
            default_temperature=default_temperature,
            default_max_tokens=default_max_tokens,
        )

    def classify_intent(self, user_message: str) -> Literal["rag", "general"]:
        """의도 분류를 수행하고 `rag/general` 중 하나를 반환합니다."""
        classify_messages = [
            SystemMessage(
                content=(
                    "너는 질의 라우터다.\n"
                    "규칙:\n"
                    "1) 문서/근거/검색/참조/출처/요약 요청이 있으면 rag\n"
                    "2) 일반 대화/창작/간단 설명은 general\n"
                    "출력은 반드시 JSON 한 줄만 사용한다.\n"
                    '허용 출력: {"intent":"rag"} 또는 {"intent":"general"}\n'
                    "다른 키 금지, 설명 금지, 코드블록 금지."
                )
            ),
            HumanMessage(content=f"질문: {user_message}"),
        ]
        response = self._chat_model.invoke(classify_messages, temperature=0.0, max_tokens=32)
        return parse_intent(str(response.content))

    def generate_text(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """non-stream 최종 텍스트를 생성합니다."""
        temperature_value = (
            temperature if temperature >= 0 else self._default_temperature
        )
        max_tokens_value = max_tokens if max_tokens > 0 else self._default_max_tokens
        lc_messages = self._to_langchain_messages(messages)
        response = self._chat_model.invoke(
            lc_messages,
            temperature=temperature_value,
            max_tokens=max_tokens_value,
        )
        return str(response.content)

    def stream_text(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Iterator[str]:
        """stream 최종 텍스트를 chunk 단위로 생성합니다."""
        temperature_value = (
            temperature if temperature >= 0 else self._default_temperature
        )
        max_tokens_value = max_tokens if max_tokens > 0 else self._default_max_tokens
        lc_messages = self._to_langchain_messages(messages)
        for chunk in self._chat_model.stream(
            lc_messages,
            temperature=temperature_value,
            max_tokens=max_tokens_value,
        ):
            content = str(chunk.content)
            if content:
                yield content

    def _to_langchain_messages(self, messages: list[dict[str, str]]) -> list[BaseMessage]:
        """dict 메시지를 LangChain 메시지로 변환합니다."""
        converted: list[BaseMessage] = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "system":
                converted.append(SystemMessage(content=content))
            elif role == "assistant":
                converted.append(AIMessage(content=content))
            else:
                converted.append(HumanMessage(content=content))
        return converted
