from __future__ import annotations


class FlightSearchSessionService:
    """
    Persistent flight-search state using the existing
    PersistentConversationStore instance.

    The conversation store is imported lazily inside methods
    to avoid circular imports during application startup.
    """

    @staticmethod
    def _store():
        from core.dependencies import conversation_store

        return conversation_store

    def get(
        self,
        user_id: str,
        session_id: str,
    ) -> dict:
        return self._store().get_flight_search(
            user_id=user_id,
            session_id=session_id,
        )

    def save(
        self,
        user_id: str,
        session_id: str,
        flight_search: dict,
    ) -> None:
        self._store().save_flight_search(
            user_id=user_id,
            session_id=session_id,
            flight_search_data=flight_search,
        )

    def clear(
        self,
        user_id: str,
        session_id: str,
    ) -> None:
        self._store().clear_flight_search(
            user_id=user_id,
            session_id=session_id,
        )

    @staticmethod
    def merge(
        existing: dict,
        new_data: dict,
    ) -> dict:
        merged = dict(existing)

        for key, value in new_data.items():
            if value is None:
                continue

            if isinstance(value, str) and not value.strip():
                continue

            merged[key] = value

        return merged


flight_search_session_service = (
    FlightSearchSessionService()
)