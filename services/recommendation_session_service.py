from core.dependencies import conversation_store


class RecommendationSessionService:
    """SQLite-backed recommendation session service. Survives server restarts."""

    def get(self, session_id: str) -> dict:
        """Returns persisted recommendation details for a session."""
        return conversation_store.get_recommendation(session_id)

    def save(self, session_id: str, recommendation: dict) -> None:
        """Persists recommendation details to SQLite."""
        conversation_store.save_recommendation(session_id, recommendation)

    def clear(self, session_id: str) -> None:
        """Removes recommendation session data after booking is initiated."""
        conversation_store.clear_recommendation(session_id)


recommendation_session_service = RecommendationSessionService()