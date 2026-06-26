from auth.schemas import CurrentUser
from langchain_components.routing.intent_types import IntentType


class AuthorizationService:
    """
    Controls which AI workflows are accessible
    for guests and authenticated users.
    """

    GUEST_ALLOWED = {
        IntentType.FAQ,
        IntentType.KNOWLEDGE_SEARCH,
        IntentType.RECOMMENDATION,
        IntentType.PRICING,
        IntentType.POLICY,
        IntentType.GENERAL,
    }

    def is_allowed(
        self,
        user: CurrentUser,
        intent: IntentType,
    ) -> bool:

        if not user.is_guest:
            return True

        return intent in self.GUEST_ALLOWED

    def unauthorized_message(
        self,
        intent: IntentType,
    ) -> str:

        messages = {
            IntentType.BOOKING:
                (
                    "I can help you plan your trip and recommend vehicles. "
                    "Please sign in to complete your booking."
                ),

            IntentType.BOOKING_STATUS:
                (
                    "Please sign in to check your booking status."
                ),
        }

        return messages.get(
            intent,
            "Please sign in to continue.",
        )


authorization_service = AuthorizationService()