from core.dependencies import conversation_store


class RecommendationSessionService:
    """SQLite-backed recommendation session service. Survives server restarts."""

    def get(self, user_id: str, session_id: str) -> dict:
        """Returns persisted recommendation details for a user's session."""
        return conversation_store.get_recommendation(user_id=user_id, session_id=session_id)

    def save(self, user_id: str, session_id: str, recommendation: dict) -> None:
        """Persists recommendation details to SQLite."""
        conversation_store.save_recommendation(
            user_id=user_id,
            session_id=session_id,
            recommendation=recommendation,
        )

    def clear(self, user_id: str, session_id: str) -> None:
        """Removes recommendation session data after booking is initiated."""
        conversation_store.clear_recommendation(user_id=user_id, session_id=session_id)


recommendation_session_service = RecommendationSessionService()