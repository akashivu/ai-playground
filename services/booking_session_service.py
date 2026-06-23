class BookingSessionService:
    """Merges booking details across multiple conversation turns."""

    def __init__(self):
        self.sessions: dict[str, dict] = {}

    def get_booking(self,session_id: str,) -> dict:
        return self.sessions.get(session_id, {})

    def save_booking(self,session_id: str,booking_details: dict,) -> None:self.sessions[session_id] = booking_details

    def clear_booking(self,session_id: str,) -> None:self.sessions.pop(session_id, None)

    def merge_booking(self,existing: dict,new_data: dict,) -> dict:

        merged = dict(existing)

        for key, value in new_data.items():
            if value is not None and value != "":
                merged[key] = value

        return merged