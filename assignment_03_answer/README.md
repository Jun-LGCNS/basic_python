# FastAPI + LangGraph 과제 가이드 (단계형)

이 문서는 학습/구현 가이드입니다.  
핵심 목표는 다음 2가지를 순차적으로 완성하는 것입니다.

- SQLite 기반 Chat History CRUD
- BaseChatModel 상속 기반 LLM 호출 + LangGraph 분기 처리

동시에 한 번에 구현하지 말고, 아래 순서대로 구현하세요.

## 1. 과제 목표

### 최종 기능 목표
- `POST /api/v1/chat/completions`에서 사용자 질문을 받아 처리한다.
- LangGraph에서 `의도 분류` 후:
  - `rag`면 mock RAG 문서(3개)를 컨텍스트로 사용한다.
  - `general`이면 일반 생성 경로로 진행한다.
- 최종 응답 생성은 LLM 호출로 처리한다.
- `stream=true`일 때 SSE로 chunk + final 이벤트를 반환한다.
- Chat History는 SQLite에 저장/조회/수정/삭제/전체삭제 가능해야 한다.

### 학습 목표
- FastAPI 계층 분리 (`api/services/repositories/core/models`)
- SQLite CRUD 쿼리 설계
- 예외 처리와 에러 응답 표준화
- `BaseChatModel` 상속 커스텀 구현
- 통합 테스트와 단위 성격 테스트 분리

## 2. 구현 순서 (중요)

아래 순서를 지키는 것을 권장합니다.

1. `CRUD 먼저`
2. `LLM(BaseChatModel) 다음`
3. `LangGraph 분기 + chat completion 오케스트레이션 마지막`

이 순서가 좋은 이유:
- CRUD를 먼저 고정하면 외부 LLM 이슈와 분리해서 디버깅 가능
- LLM 단계에서 실패해도 DB/API 기본 동작이 이미 보장됨
- 마지막에 분기 흐름만 연결하면 되므로 복잡도가 크게 줄어듦

## 3. 단계별 구현 가이드

## 3-1. 1단계: Chat History CRUD

### 구현 대상
- 저장소: `src/repositories/chat_history_repository.py`
- 서비스: `src/services/chat_history_service.py`
- 라우터: `src/api/histories.py`
- 모델: `src/models/history.py`

### 구현 요구사항
- `session_id + query_id` 복합 PK 유일 제약
- 조회 정렬: `query_id ASC`
- `lt_query_id` 필터 지원 (`query_id < lt_query_id`)
- 기본 `limit=5`
- 전체 삭제 API: `DELETE /api/v1/chat-histories`

### 체크리스트
- [ ] 생성 성공(201)
- [ ] 중복 생성 충돌(409)
- [ ] 목록 조회/필터 조회 동작
- [ ] 수정/단건조회/삭제 동작
- [ ] 전체 삭제 후 건수 반환

## 3-2. 2단계: BaseChatModel 기반 LLM 호출

### 구현 대상
- `src/services/langchain_chat_model.py`
- `src/services/llm_gateway.py`

### 구현 요구사항
- `EndpointChatModel(BaseChatModel)` 구현
- non-stream: `_generate` + HTTP POST
- stream: `_stream` + SSE 파싱
- `llm_gateway`는 위 모델을 사용해:
  - 의도 분류 호출
  - 최종 생성 호출
  - 스트림 생성 호출

### 의도 분류 프롬프트 규칙
- 반드시 JSON 한 줄 출력 강제
- 허용 출력:
  - `{"intent":"rag"}`
  - `{"intent":"general"}`

### 체크리스트
- [ ] HTTP 에러 시 상태코드/응답본문 일부를 로깅
- [ ] JSON 파싱 실패 시 원인 로깅
- [ ] `intent` 파싱 실패 시 안전하게 `general` 폴백

## 3-3. 3단계: LangGraph 분기 + Completion 연결

### 구현 대상
- 그래프: `src/services/rag_graph/*`
- 오케스트레이션: `src/services/chat_completion_service.py`
- 라우터: `src/api/chat.py`

### 분기 흐름
- 사용자 입력
- 의도 분류 노드
- `rag` -> mock 문서 3개 주입
- `general` -> 문서 비움
- 최종 생성 노드(LLM 호출)

### stream 응답 포맷
- chunk:
```text
data: {"chunk":"..."}
```
- final:
```text
data: {"final_answer":"...","documents":[...],"intent":"rag","session_id":1,"query_id":10}
```

## 4. NotImplemented 과제 템플릿 권장 위치

아래 함수들을 `raise NotImplementedError`로 열어두고 학습자가 구현하게 하는 구성이 좋습니다.

### CRUD 단계
- `chat_history_repository.py`
  - `list_before_query_id`
  - `update`
  - `delete_all`
- `chat_history_service.py`
  - `create_history`의 `IntegrityError -> ConflictError` 변환
  - `list_histories` 분기 로직
  - `delete_all_histories`
- `api/histories.py`
  - `list_histories`
  - `delete_all_histories`

### LLM 단계
- `langchain_chat_model.py`
  - `_build_payload`
  - `_post_json`
  - `_stream`
- `llm_gateway.py`
  - `classify_intent`
  - `generate_text`
  - `stream_text`

### 분기/오케스트레이션 단계
- `rag_graph/nodes.py`
  - `ClassifyIntentNode.__call__`
  - `route_after_intent`
- `chat_completion_service.py`
  - `create_completion`
  - `stream_completion`
  - `_build_final_messages`

## 5. API 스펙 요약

### Chat Completion
- `POST /api/v1/chat/completions`
- request 예시:
```json
{
  "session_id": 1001,
  "query_id": 10,
  "message": "LangGraph에 대해 RAG로 검색해서 알려줘.",
  "stream": false,
  "temperature": 0.6,
  "max_tokens": 200
}
```

### History CRUD
- `POST /api/v1/chat-histories`
- `GET /api/v1/chat-histories?session_id=1001&lt_query_id=10&limit=5`
- `GET /api/v1/chat-histories/{session_id}/{query_id}`
- `PATCH /api/v1/chat-histories/{session_id}/{query_id}`
- `DELETE /api/v1/chat-histories/{session_id}/{query_id}`
- `DELETE /api/v1/chat-histories` (전체 삭제)

## 6. 테스트 전략 (파일 분리)

### 1) DB 로직 검증
- 파일: `tests/test_chat_history_api.py`
- 목적: CRUD, 중복조건, 전체삭제 검증
- 외부 LLM 의존 없음

### 2) 실제 LLM 통합 검증
- 파일: `tests/test_chat_llm_integration_api.py`
- 목적: 실제 엔드포인트 기준 분기/stream 동작 확인
- 검증 포인트:
  - RAG 질문: `intent=="rag"` + `documents` 존재
  - 일반 질문: `intent=="general"` + `documents==[]`
  - 응답 본문 내용 자체는 검증하지 않음

## 7. 실행 방법

```powershell
uv venv .venv
uv sync
uv run uvicorn src.main:app --reload
```

Swagger:
- `http://127.0.0.1:8000/docs`

## 8. pytest 실행 방법

전체 테스트:
```powershell
uv run pytest -q
```

DB 테스트만:
```powershell
uv run pytest -q tests/test_chat_history_api.py
```

실제 LLM 통합 테스트만:
```powershell
uv run pytest -q tests/test_chat_llm_integration_api.py
```

## 9. 환경 변수

- `RAG_DB_PATH` (기본: `data/chat_history.db`)
- `LLM_ENDPOINT`
- `LLM_MODEL`
- `LLM_TEMPERATURE`
- `LLM_MAX_TOKENS`
- `LLM_TIMEOUT_SECONDS`

## 10. 제출 기준 예시

- [ ] API가 스펙대로 동작한다.
- [ ] 에러 응답이 일관된 형태다.
- [ ] 로그에서 DB 조회/LLM 실패 원인을 확인할 수 있다.
- [ ] `pytest` 전체 통과한다.
- [ ] 파일 길이 200줄 제한을 지킨다.

