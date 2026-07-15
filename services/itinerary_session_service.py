from core.dependencies import conversation_store


class ItinerarySessionService:

    def get(
        self,
        user_id: str,
        session_id: str,
    ) -> dict:
        return conversation_store.get_itinerary(
            user_id=user_id,
            session_id=session_id,
        )

    def save(
        self,
        user_id: str,
        session_id: str,
        itinerary: dict,
    ) -> None:
        conversation_store.save_itinerary(
            user_id=user_id,
            session_id=session_id,
            itinerary_data=itinerary,
        )

    def clear(
        self,
        user_id: str,
        session_id: str,
    ) -> None:
        conversation_store.clear_itinerary(
            user_id=user_id,
            session_id=session_id,
        )

    def merge(
        self,
        existing: dict,
        new_data: dict,
    ) -> dict:
        merged = dict(existing)

        for key, value in new_data.items():
            if value is not None and value != "":
                merged[key] = value

        return merged


itinerary_session_service = (
    ItinerarySessionService()
)