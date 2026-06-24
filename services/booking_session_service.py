from core.dependencies import conversation_store


class BookingSessionService:
    """SQLite-backed booking session service. Survives server restarts."""

    def get_booking(self, session_id: str) -> dict:
        """Returns persisted booking details for a session."""
        return conversation_store.get_booking(session_id)

    def save_booking(self, session_id: str, booking_details: dict) -> None:
        """Persists booking details to SQLite."""
        conversation_store.save_booking(session_id, booking_details)

    def clear_booking(self, session_id: str) -> None:
        """Removes booking session data."""
        conversation_store.clear_booking(session_id)

    def merge_booking(self, existing: dict, new_data: dict) -> dict:
        """Merges new non-null values into existing booking details."""
        merged = dict(existing)
        for key, value in new_data.items():
            if value is not None and value != "":
                merged[key] = value
        return merged


booking_session_service = BookingSessionService()