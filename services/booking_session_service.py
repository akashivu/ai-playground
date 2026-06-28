from core.dependencies import conversation_store

class BookingSessionService:
    """
    Service responsible for persisting booking details
    during a multi-turn booking conversation.
    Booking state is stored per authenticated user
    and per chat session.
    """
    def get_booking(self, user_id: str, session_id: str) -> dict:
        """
        Returns persisted booking details
        for a user's conversation.
        """
        return conversation_store.get_booking(
            user_id=user_id,
            session_id=session_id,
        )

    def save_booking(self, user_id: str, session_id: str, booking: dict) -> None:
        """
        Persists booking details.
        """
        conversation_store.save_booking(
            user_id=user_id,
            session_id=session_id,
            booking_data=booking,
        )

    def clear_booking(self, user_id: str, session_id: str) -> None:
        """
        Removes persisted booking details.
        """
        conversation_store.clear_booking(
            user_id=user_id,
            session_id=session_id,
        )

    @staticmethod
    def merge_booking(existing: dict, new_data: dict) -> dict:
        """
        Merges newly extracted booking
        fields into the existing booking state.
        Existing values are preserved unless
        a new non-empty value is provided.
        """
        merged = dict(existing)
        for key, value in new_data.items():
            if value is None:
                continue
            if isinstance(value, str) and not value.strip():
                continue
            merged[key] = value
        return merged

booking_session_service = BookingSessionService()