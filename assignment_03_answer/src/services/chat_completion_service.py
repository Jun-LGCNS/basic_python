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
        histories = self._history_service.list_histories(
            session_id=request.session_id,
            lt_query_id=request.query_id,
            limit=5,
        )
        graph_state = self._graph_runner.run(user_message=request.message)
        intent = self._normalize_intent(graph_state.get(KEY_INTENT, "general"))
        documents = graph_state.get(KEY_DOCUMENTS, [])

        messages = self._build_final_messages(
            user_message=request.message,
            histories=histories,
            documents=documents,
            intent=intent,
        )
        answer = self._llm_gateway.generate_text(
            messages=messages,
            temperature=request.temperature or -1.0,
            max_tokens=request.max_tokens or -1,
        )

        self._history_service.create_history(
            ChatHistoryCreateRequest(
                session_id=request.session_id,
                query_id=request.query_id,
                user_message=request.message,
                intent=intent,
                final_answer=answer,
            )
        )
        return ChatCompletionResult(
            session_id=request.session_id,
            query_id=request.query_id,
            intent=intent,
            answer=answer,
            documents=documents,
        )

    def stream_completion(self, request: ChatCompletionRequest) -> Iterator[str]:
        """stream 채팅 응답을 SSE 형태로 생성하고 히스토리를 저장합니다."""
        histories = self._history_service.list_histories(
            session_id=request.session_id,
            lt_query_id=request.query_id,
            limit=5,
        )
        graph_state = self._graph_runner.run(user_message=request.message)
        intent = self._normalize_intent(graph_state.get(KEY_INTENT, "general"))
        documents = graph_state.get(KEY_DOCUMENTS, [])

        messages = self._build_final_messages(
            user_message=request.message,
            histories=histories,
            documents=documents,
            intent=intent,
        )
        answer_chunks: list[str] = []
        for chunk in self._llm_gateway.stream_text(
            messages=messages,
            temperature=request.temperature or -1.0,
            max_tokens=request.max_tokens or -1,
        ):
            answer_chunks.append(chunk)
            chunk_payload = json.dumps({"chunk": chunk}, ensure_ascii=False)
            yield f"data: {chunk_payload}\n\n"

        final_answer = "".join(answer_chunks)
        self._history_service.create_history(
            ChatHistoryCreateRequest(
                session_id=request.session_id,
                query_id=request.query_id,
                user_message=request.message,
                intent=intent,
                final_answer=final_answer,
            )
        )

        final_payload = json.dumps(
            {
                "final_answer": final_answer,
                "documents": [document.model_dump() for document in documents],
                "intent": intent,
                "session_id": request.session_id,
                "query_id": request.query_id,
            },
            ensure_ascii=False,
        )
        yield f"data: {final_payload}\n\n"

    def _build_final_messages(
        self,
        user_message: str,
        histories: list[ChatHistoryRead],
        documents: list[RagDocument],
        intent: Literal["rag", "general"],
    ) -> list[dict[str, str]]:
        """최종 생성 호출용 메시지 배열을 구성합니다."""
        history_lines = [
            f"query_id={item.query_id} user={item.user_message} assistant={item.final_answer}"
            for item in histories
        ]
        history_text = "\n".join(history_lines) if history_lines else "없음"

        document_lines = [
            f"title={doc.title} page={doc.page_number} content={doc.content}" for doc in documents
        ]
        document_text = "\n".join(document_lines) if document_lines else "없음"

        return [
            {
                "role": "system",
                "content": "너는 친절한 어시스턴트다. 주어진 히스토리와 문서를 반영해 한국어로 답변한다.",
            },
            {
                "role": "user",
                "content": (
                    f"의도={intent}\n"
                    f"이전 히스토리(ASC, 최대 5개):\n{history_text}\n\n"
                    f"RAG 문서:\n{document_text}\n\n"
                    f"현재 질문:\n{user_message}"
                ),
            },
        ]

    def _normalize_intent(self, intent: str) -> Literal["rag", "general"]:
        """의도 문자열을 허용 값으로 정규화합니다."""
        if intent == "rag":
            return "rag"
        return "general"

