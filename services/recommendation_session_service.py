class RecommendationSessionService:
    """Stores recommendation context per session for handoff to booking workflow."""

    def __init__(self) -> None:
        self.sessions: dict[str, dict] = {}

    def get(self, session_id: str) -> dict:
        """Returns stored recommendation for a session."""
        return self.sessions.get(session_id, {})

    def save(self, session_id: str, recommendation: dict) -> None:
        """Saves recommendation details for a session."""
        self.sessions[session_id] = recommendation

    def clear(self, session_id: str) -> None:
        """Clears recommendation state after booking is initiated."""
        self.sessions.pop(session_id, None)


recommendation_session_service = RecommendationSessionService()