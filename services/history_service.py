from core.dependencies import conversation_store


class HistoryService:
    """
    Service responsible for conversation history operations.

    This service acts as the business layer between
    the API routes and the persistence layer.
    """

    def list_sessions(
        self,
        user_id: str,
    ) -> list[dict]:
        """
        Returns all conversation sessions
        for a user ordered by latest activity.
        """
        return conversation_store.get_user_sessions(
            user_id=user_id,
        )

    def get_session(
        self,
        user_id: str,
        session_id: str,
    ) -> list[dict]:
        """
        Returns the complete conversation
        for the supplied session.
        """
        return conversation_store.get_session(
            user_id=user_id,
            session_id=session_id,
        )

    def delete_session(
        self,
        user_id: str,
        session_id: str,
    ) -> None:
        """
        Deletes a conversation session.
        """
        conversation_store.delete_session(
            user_id=user_id,
            session_id=session_id,
        )


history_service = HistoryService()