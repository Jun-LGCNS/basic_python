"""채팅 히스토리 SQLite 저장소 구현.

파일의 목적:
- 채팅 히스토리 도메인의 CRUD SQL 처리를 담당한다.

포함 내용:
- ChatHistoryRepository 클래스

사용 시점:
- 서비스 계층에서 DB 조회/변경이 필요할 때 사용한다.
"""

from datetime import datetime, timezone
import logging
import sqlite3

from src.models.history import ChatHistoryRead

logger = logging.getLogger(__name__)


class ChatHistoryRepository:
    """채팅 히스토리 CRUD를 수행하는 SQLite 저장소."""

    def __init__(self, database_path: str) -> None:
        self._database_path = database_path

    def create(
        self,
        session_id: int,
        query_id: int,
        user_message: str,
        intent: str,
        final_answer: str,
    ) -> ChatHistoryRead:
        """히스토리를 생성하고 생성 결과를 반환한다."""
        created_at = datetime.now(timezone.utc).isoformat()
        connection = self._connect()
        try:
            connection.execute(
                """
                INSERT INTO chat_histories (
                    session_id, query_id, user_message, intent, final_answer, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, query_id, user_message, intent, final_answer, created_at),
            )
            connection.commit()
            row = connection.execute(
                """
                SELECT session_id, query_id, user_message, intent, final_answer, created_at
                FROM chat_histories
                WHERE session_id = ? AND query_id = ?
                """,
                (session_id, query_id),
            ).fetchone()
        finally:
            connection.close()

        if row is None:
            raise RuntimeError("히스토리 생성 직후 조회에 실패했다.")
        return self._to_history(row)

    def list_before_query_id(
        self,
        session_id: int,
        query_id: int,
        limit: int = 5,
    ) -> list[ChatHistoryRead]:
        """지정 query_id보다 작은 히스토리를 오름차순으로 조회한다."""
        # Step 1. session_id와 query_id(<) 조건, ASC 정렬, LIMIT를 적용한 SQL을 작성하세요.
        # Step 2. 조회 결과를 `_to_history`로 변환하세요.
        # Step 3. logger.info로 session_id/query_id/limit/개수를 남기세요.
        connection = self._connect()
        
        try:
            cursor = connection.execute(
                """
                SELECT session_id, query_id, user_message, intent, final_answer, created_at
                FROM chat_histories
                WHERE session_id = ? AND query_id < ?
                ORDER BY query_id ASC
                LIMIT ?
                """
            ,(session_id, query_id, limit))
            rows = [self._to_history(row) for row in cursor.fetchall()]
        
        finally:
            connection.close()
        logger.info(
            "Fetched histories session_id=%s limit=%s count=%s query_ids=%s",
            session_id,
            limit,
            len(rows),
            [item.query_id for item in rows],
        )
        return rows

    def list_by_session(self, session_id: int, limit: int = 5) -> list[ChatHistoryRead]:
        """세션 기준 히스토리를 query_id 오름차순으로 조회한다."""
        connection = self._connect()
        try:
            cursor = connection.execute(
                """
                SELECT session_id, query_id, user_message, intent, final_answer, created_at
                FROM chat_histories
                WHERE session_id = ?
                ORDER BY query_id ASC
                LIMIT ?
                """,
                (session_id, limit),
            )
            rows = [self._to_history(row) for row in cursor.fetchall()]
        finally:
            connection.close()

        logger.info(
            "Fetched histories session_id=%s limit=%s count=%s query_ids=%s",
            session_id,
            limit,
            len(rows),
            [item.query_id for item in rows],
        )
        return rows

    def get(self, session_id: int, query_id: int) -> ChatHistoryRead | None:
        """세션/쿼리 ID로 히스토리 단건을 조회한다."""
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT session_id, query_id, user_message, intent, final_answer, created_at
                FROM chat_histories
                WHERE session_id = ? AND query_id = ?
                """,
                (session_id, query_id),
            ).fetchone()
        finally:
            connection.close()

        if row is None:
            return None
        return self._to_history(row)

    def update(
        self,
        session_id: int,
        query_id: int,
        user_message: str | None = None,
        intent: str | None = None,
        final_answer: str | None = None,
    ) -> ChatHistoryRead | None:
        """히스토리를 수정하고 수정 결과를 반환한다."""
        # Step 1. 현재 히스토리를 조회하고 없으면 None을 반환하세요.
        # Step 2. 전달하지 않은 필드는 기존 값으로 유지하세요.
        # Step 3. UPDATE 후 commit하고 최신 값을 다시 조회해 반환하세요.
        current = self.get(session_id, query_id)
        if current == None:
            return None
        else:
            new_message = user_message if user_message is not None else current.user_message
            new_intent = intent if intent is not None else current.intent
            new_final_answer = final_answer if final_answer is not None else current.final_answer
            
            connection = self._connect()
            try:
                connection.execute(
                """UPDATE chat_histories
                SET user_message = ?, intent = ?, final_answer = ?
                WHERE session_id = ? AND query_id = ?""",
                (new_message, new_intent, new_final_answer, session_id, query_id),
                )
                connection.commit()

            finally:
                connection.close()

            return self.get(session_id, query_id)
            raise NotImplementedError("update를 구현하세요.")

    def delete(self, session_id: int, query_id: int) -> bool:
        """히스토리를 삭제하고 삭제 여부를 반환한다."""
        connection = self._connect()
        try:
            cursor = connection.execute(
                """
                DELETE FROM chat_histories
                WHERE session_id = ? AND query_id = ?
                """,
                (session_id, query_id),
            )
            connection.commit()
            deleted = cursor.rowcount > 0
        finally:
            connection.close()
        return deleted

    def delete_all(self) -> int:
        """히스토리 전체를 삭제하고 삭제된 개수를 반환한다."""
        # Step 1. 전체 DELETE를 실행하세요.
        # Step 2. rowcount를 사용해 삭제 개수를 계산하고 commit하세요.
        # Step 3. logger.info에 삭제 개수를 남기고 반환하세요.
        connection = self._connect()
        try:
            cursor = connection.execute(
                """
                DELETE FROM chat_histories
                """
            )
            row_count = cursor.rowcount
            connection.commit()
        finally:
            connection.close()
        logger.info("Deleted all histories count=%s", row_count)
        return row_count
        raise NotImplementedError("delete_all을 구현하세요.")

    def _connect(self) -> sqlite3.Connection:
        """SQLite 연결을 생성해 반환한다."""
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _to_history(self, row: sqlite3.Row) -> ChatHistoryRead:
        """SQLite row를 히스토리 모델로 변환한다."""
        return ChatHistoryRead(
            session_id=row["session_id"],
            query_id=row["query_id"],
            user_message=row["user_message"],
            intent=row["intent"],
            final_answer=row["final_answer"],
            created_at=row["created_at"],
        )
