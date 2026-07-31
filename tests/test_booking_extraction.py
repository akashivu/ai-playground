import asyncio

from langchain_components.agents import agent_registry
from langchain_components.conversation import ConversationContext, ConversationManager

import langchain_components.agents.booking_agent  # noqa: F401

from services.booking_session_service import booking_session_service


async def main() -> None:
    session_id = "extraction_test_1"
    booking_session_service.clear_booking(user_id="u1", session_id=session_id)

    manager = ConversationManager(memory=None, agent_registry=agent_registry)
    context = ConversationContext(user_id="u1", session_id=session_id)

    message = (
        "My name is Asha Rao, email asha@example.com, mobile 9876543210. "
        "I need an Airport Transfer, One Way, from Koramangala to "
        "Bengaluru Airport on 25 July 2026 at 6:00 AM in a Sedan."
    )

    result = await manager.handle_message(
        {"intent": "booking_agent", "message": message}, context
    )

    print("success:", result.success)
    print("response:", result.response)
    print("completed:", result.agent_result.metadata.get("completed"))
    print("booking_details:", result.agent_result.metadata.get("booking_details"))

    if not result.success:
        print("error:", result.error)


if __name__ == "__main__":
    asyncio.run(main())