from __future__ import annotations

from core.dependencies import conversation_store


class FlightSearchSessionService:
    """
    Persistent flight-search state for multi-turn conversations.

    State is scoped by user_id + session_id and survives
    application restarts because it is stored in the
    existing SQLite conversation database.
    """

    def get(
        self,
        user_id: str,
        session_id: str,
    ) -> dict:
        return conversation_store.get_flight_search(
            user_id=user_id,
            session_id=session_id,
        )

    def save(
        self,
        user_id: str,
        session_id: str,
        flight_search: dict,
    ) -> None:
        conversation_store.save_flight_search(
            user_id=user_id,
            session_id=session_id,
            flight_search_data=flight_search,
        )

    def clear(
        self,
        user_id: str,
        session_id: str,
    ) -> None:
        conversation_store.clear_flight_search(
            user_id=user_id,
            session_id=session_id,
        )

    @staticmethod
    def merge(
        existing: dict,
        new_data: dict,
    ) -> dict:
        """
        Merge only meaningful new values.

        Existing values are preserved when the new extraction
        returns None or an empty string.
        """
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