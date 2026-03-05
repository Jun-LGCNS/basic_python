"""채팅 완성 유스케이스 서비스.

이 파일의 목적:
- 의도 분류 분기 + 최종 LLM 생성 + 히스토리 저장 흐름을 조율합니다.

포함 내용:
- ChatCompletionService 클래스

사용 시점:
- 채팅 완성 라우터에서 non-stream/stream 요청을 처리할 때 사용합니다.
"""

from collections.abc import Iterator
import json
from typing import Literal

from src.models.chat import ChatCompletionRequest, ChatCompletionResult, RagDocument
from src.models.history import ChatHistoryCreateRequest, ChatHistoryRead
from src.services.chat_history_service import ChatHistoryService
from src.services.llm_gateway import LlmGateway
from src.services.rag_graph.run import ChatGraphRunner
from src.services.rag_graph.state_keys import KEY_DOCUMENTS, KEY_INTENT


class ChatCompletionService:
    """의도 분기 기반 채팅 완성 서비스."""

    def __init__(
        self,
        llm_gateway: LlmGateway,
        history_service: ChatHistoryService,
        graph_runner: ChatGraphRunner,
    ) -> None:
        self._llm_gateway = llm_gateway
        self._history_service = history_service
        self._graph_runner = graph_runner

    def create_completion(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        """non-stream 채팅 응답을 생성하고 히스토리를 저장합니다."""
        # Step 1. query_id보다 작은 히스토리(ASC, limit=5)를 조회하세요.
        # Step 2. graph_runner로 intent/documents를 계산하세요.
        # Step 3. `_build_final_messages`로 프롬프트를 만들고 generate_text를 호출하세요.
        # Step 4. 최종 답변을 히스토리에 저장하세요.
        # Step 5. ChatCompletionResult를 반환하세요.
        histories: list[ChatHistoryRead] = self._history_service.list_histories(
            session_id=request.session_id,
            lt_query_id=request.query_id,
            limit=5,
        )
        state = self._graph_runner.run(request.message)
        print(state)
        intent = self._normalize_intent(state.get(KEY_INTENT, "general"))

        documents: list[RagDocument] = state.get(KEY_DOCUMENTS, []) or []
        messages = self._build_final_messages(
            message=request.message,
            histories=histories,
            documents=documents,
            intent=intent,
        )
        final_answer: str = self._llm_gateway.generate_text(messages = messages,
        temperature = request.temperature,
        max_tokens = request.max_tokens)
        self._history_service.create_history(
            ChatHistoryCreateRequest(
                session_id=request.session_id,
                query_id=request.query_id,
                user_message=request.message,
                intent=intent,
                final_answer=final_answer,
            )
        )
        return ChatCompletionResult(
            session_id=request.session_id,
            query_id=request.query_id,
            intent=intent,
            documents=documents,
            answer=final_answer,
        )

    def stream_completion(self, request: ChatCompletionRequest) -> Iterator[str]:
        """stream 채팅 응답을 SSE 형태로 생성하고 히스토리를 저장합니다."""
        # Step 1. non-stream과 동일하게 히스토리/분기/최종 프롬프트를 준비하세요.
        # Step 2. stream_text를 순회하며 `data: {"chunk":"..."}` 이벤트를 yield 하세요.
        # Step 3. 모든 chunk를 합쳐 final_answer를 만들고 히스토리에 저장하세요.
        # Step 4. `final_answer/documents/intent/session_id/query_id`를 final 이벤트로 yield 하세요.
        histories: list[ChatHistoryRead] = self._history_service.list_histories(
            session_id=request.session_id,
            lt_query_id=request.query_id,
            limit=5,
        )

        state = self._graph_runner.run(user_message=request.message)
        intent = self._normalize_intent(state.get(KEY_INTENT, "general"))
        documents: list[RagDocument] = state.get(KEY_DOCUMENTS, []) or []

        messages = self._build_final_messages(
            message=request.message,
            histories=histories,
            documents=documents,
            intent=intent,
        )

        # Step 2. stream_text를 순회하며 `data: {"chunk":"..."}` 이벤트를 yield 하세요.
        chunks: list[str] = []
        for chunk in self._llm_gateway.stream_text(messages,
            temperature=request.temperature if request.temperature is not None else 0.7,
            max_tokens=request.max_tokens if request.max_tokens is not None else 512):
            chunks.append(chunk)
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"

        # Step 3. 모든 chunk를 합쳐 final_answer를 만들고 히스토리에 저장하세요.
        final_answer = "".join(chunks)

        self._history_service.create_history(
            ChatHistoryCreateRequest(
                session_id=request.session_id,
                query_id=request.query_id,
                user_message=request.message,
                intent=intent,
                final_answer=final_answer,
            )
        )

        # Step 4. `final_answer/documents/intent/session_id/query_id`를 final 이벤트로 yield 하세요.
        yield (
            "data: "
            + json.dumps(
                {
                    "final_answer": final_answer,
                    "documents": [d.model_dump() if hasattr(d, "model_dump") else d for d in documents],
                    "intent": intent,
                    "session_id": request.session_id,
                    "query_id": request.query_id,
                },
                ensure_ascii=False,
            )
            + "\n\n"
        )

    def _build_final_messages(
        self,
        message: str,
        histories: list[ChatHistoryRead],
        documents: list[RagDocument],
        intent: Literal["rag", "general"],
    ) -> list[dict[str, str]]:
        """최종 생성 호출용 메시지 배열을 구성합니다."""
        # Step 1. histories를 줄 단위 문자열로 직렬화하세요.
        # Step 2. documents를 줄 단위 문자열로 직렬화하세요.
        # Step 3. system/user 메시지 2개를 만들어 list[dict]로 반환하세요.
        # Step 1. histories를 줄 단위 문자열로 직렬화하세요.
        history_lines: list[str] = []
        for h in histories:
            # ChatHistoryRead의 실제 필드명은 프로젝트마다 다를 수 있어 getattr로 안전 처리
            um = getattr(h, "message", "") or ""
            fa = getattr(h, "final_answer", "") or ""
            if um:
                history_lines.append(f"user: {um}")
            if fa:
                history_lines.append(f"assistant: {fa}")
        histories_text = "\n".join(history_lines).strip()

        # Step 2. documents를 줄 단위 문자열로 직렬화하세요.
        doc_lines: list[str] = []
        for i, d in enumerate(documents, start=1):
            title = getattr(d, "title", "") or ""
            content = getattr(d, "content", "") or ""
            if title:
                doc_lines.append(f"[{i}] {title} - {content}".strip())
            else:
                doc_lines.append(f"[{i}] {content}".strip())
        documents_text = "\n".join(doc_lines).strip()

        # Step 3. system/user 메시지 2개를 만들어 list[dict]로 반환하세요.
        if intent == "rag":
            system_content = (
                "너는 도움이 되는 어시스턴트다.\n"
                "아래 대화 히스토리와 참고 문서를 근거로 답하라.\n"
                "문서에 없는 내용은 추측하지 말고, 모르면 모른다고 말하라.\n\n"
                f"[대화 히스토리]\n{histories_text}\n\n"
                f"[참고 문서]\n{documents_text}"
            ).strip()
        else:
            system_content = (
                "너는 도움이 되는 어시스턴트다.\n"
                "아래 대화 히스토리를 참고해 정확하고 자연스럽게 답하라.\n\n"
                f"[대화 히스토리]\n{histories_text}"
            ).strip()

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": message},
        ]

    def _normalize_intent(self, intent: str) -> Literal["rag", "general"]:
        """의도 문자열을 허용 값으로 정규화합니다."""
        if intent == "rag":
            return "rag"
        return "general"

