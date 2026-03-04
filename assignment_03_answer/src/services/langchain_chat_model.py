"""LangChain BaseChatModel 기반 원격 LLM 모델."""

from collections.abc import Iterator
import json
import logging
from typing import Any

import httpx
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field

from src.core.errors import UpstreamServiceError
from src.services.llm_parsing import extract_text_from_stream_chunk

logger = logging.getLogger(__name__)


class EndpointChatModel(BaseChatModel):
    """외부 엔드포인트를 호출하는 BaseChatModel 구현."""

    endpoint: str
    model_name: str
    request_timeout: float = 30.0
    default_temperature: float = 0.6
    default_max_tokens: int = 200
    headers: dict[str, str] = Field(
        default_factory=lambda: {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
    )

    @property
    def _llm_type(self) -> str:
        return "endpoint-chat-model"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        del stop, run_manager
        payload = self._build_payload(messages=messages, stream=False, **kwargs)
        response_json = self._post_json(payload)
        content = self._extract_completion_text(response_json)
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=content))],
            llm_output={"raw_response": response_json},
        )

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        del stop
        payload = self._build_payload(messages=messages, stream=True, **kwargs)
        try:
            with httpx.Client(timeout=self.request_timeout) as client:
                with client.stream(
                    "POST", self.endpoint, headers=self.headers, json=payload
                ) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        raw_payload = line[5:].strip()
                        if not raw_payload or raw_payload == "[DONE]":
                            continue
                        parsed = json.loads(raw_payload)
                        delta = extract_text_from_stream_chunk(parsed)
                        if not delta:
                            continue
                        if run_manager:
                            run_manager.on_llm_new_token(delta)
                        yield ChatGenerationChunk(message=AIMessageChunk(content=delta))
        except httpx.HTTPStatusError as error:
            body = error.response.text[:500]
            logger.exception(
                "LLM stream HTTP error endpoint=%s status=%s body=%s",
                self.endpoint,
                error.response.status_code,
                body,
            )
            raise UpstreamServiceError(
                "LLM 스트리밍 호출에 실패했습니다.",
                {
                    "endpoint": self.endpoint,
                    "status_code": error.response.status_code,
                    "response_body": body,
                },
            ) from error
        except (httpx.HTTPError, json.JSONDecodeError) as error:
            logger.exception("LLM stream call failed endpoint=%s", self.endpoint)
            raise UpstreamServiceError(
                "LLM 스트리밍 호출에 실패했습니다.",
                {"endpoint": self.endpoint, "reason": str(error)},
            ) from error

    def _build_payload(
        self,
        messages: list[BaseMessage],
        stream: bool,
        **kwargs: Any,
    ) -> dict[str, object]:
        temperature = kwargs.get("temperature", self.default_temperature)
        max_tokens = kwargs.get("max_tokens", self.default_max_tokens)
        return {
            "messages": [self._to_openai_message(message) for message in messages],
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "stream": stream,
            "model": self.model_name,
        }

    def _post_json(self, payload: dict[str, object]) -> dict[str, object]:
        try:
            response = httpx.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as error:
            body = error.response.text[:500]
            logger.exception(
                "LLM HTTP error endpoint=%s status=%s body=%s",
                self.endpoint,
                error.response.status_code,
                body,
            )
            raise UpstreamServiceError(
                "LLM 호출에 실패했습니다.",
                {
                    "endpoint": self.endpoint,
                    "status_code": error.response.status_code,
                    "response_body": body,
                },
            ) from error
        except json.JSONDecodeError as error:
            logger.exception("LLM JSON parse failed endpoint=%s", self.endpoint)
            raise UpstreamServiceError(
                "LLM 응답 JSON 파싱에 실패했습니다.",
                {"endpoint": self.endpoint, "reason": str(error)},
            ) from error
        except httpx.HTTPError as error:
            logger.exception("LLM call failed endpoint=%s", self.endpoint)
            raise UpstreamServiceError(
                "LLM 호출에 실패했습니다.",
                {"endpoint": self.endpoint, "reason": str(error)},
            ) from error

    def _extract_completion_text(self, payload: dict[str, object]) -> str:
        choices = payload.get("choices")
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            first = choices[0]
            message = first.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
            text = first.get("text")
            if isinstance(text, str):
                return text
        return ""

    def _to_openai_message(self, message: BaseMessage) -> dict[str, str]:
        role = message.type
        if role == "human":
            role = "user"
        elif role == "ai":
            role = "assistant"
        elif role not in {"system", "user", "assistant"}:
            role = "user"
        content = message.content if isinstance(message.content, str) else str(message.content)
        return {"role": role, "content": content}

