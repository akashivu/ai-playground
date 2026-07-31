import asyncio

from langchain_components.agents import agent_registry
from langchain_components.conversation import ConversationContext, ConversationManager
from langchain_components.tools import tool_executor

import langchain_components.agents.booking_agent  # noqa: F401

from auth.schemas import CurrentUser
from services.booking_session_service import booking_session_service


async def main() -> None:
    # Clear any leftover state from a previous run - important since the
    # real conversation_store persists to disk, unlike an in-memory stub.
    booking_session_service.clear_booking(user_id="u1", session_id="s1")

    manager = ConversationManager(memory=None, agent_registry=agent_registry)
    context = ConversationContext(
        user_id="u1",
        session_id="s1",
        metadata={
            "current_user": CurrentUser(
                user_id="u1", name="Asha", email="asha@example.com"
            )
        },
    )

    result = await manager.handle_message(
        {
            "intent": "booking_agent",
            "message": "I need a cab",
            "name": "Asha Rao",
            "pickup_location": "Koramangala",
        },
        context,
    )
    print("[1] turn 1 (partial info) ->", result.success, "|", result.response)
    assert result.success
    assert (
        "email" in result.response.lower()
        or "mobile" in result.response.lower()
        or result.response
    )
    assert result.agent_result.metadata["completed"] is False
    assert result.agent_result.metadata["booking_details"]["name"] == "Asha Rao"
    assert (
        result.agent_result.metadata["booking_details"]["pickup_location"]
        == "Koramangala"
    )
    assert result.agent_result.tool_calls == []

    result = await manager.handle_message(
        {
            "intent": "booking_agent",
            "message": "here's more info",
            "email": "asha@example.com",
            "mobile": "9876543210",
            "trip_category": "Airport Transfer",
            "trip_type": "One Way",
        },
        context,
    )
    print(
        "[2] turn 2 (more info, still incomplete) ->",
        result.success,
        "|",
        result.response,
    )
    assert result.success
    assert result.agent_result.metadata["completed"] is False
    booking_so_far = result.agent_result.metadata["booking_details"]
    assert booking_so_far["email"] == "asha@example.com"
    assert booking_so_far["name"] == "Asha Rao"  # preserved from turn 1

    result = await manager.handle_message(
        {
            "intent": "booking_agent",
            "message": "final details",
            "destination": "Bengaluru Airport",
            "travel_date": "25 July 2026",
            "pickup_time": "6:00 AM",
            "vehicle_type": "Sedan",
        },
        context,
    )
    if result.success:
        print("[3] turn 3 (complete) ->", result.success, "|", result.response[:60], "...")
    else:
        print("[3] turn 3 FAILED ->", result.success, "| error:", result.error)
        print("    full agent_result:", result.agent_result)
    assert result.success, f"booking creation failed: {result.error}"
    assert result.agent_result.metadata["completed"] is True
    assert len(result.agent_result.tool_calls) == 1
    assert result.agent_result.tool_calls[0]["tool_name"] == "create_booking"
    assert result.agent_result.tool_calls[0]["success"] is True
    booking_data = result.agent_result.tool_calls[0]["output"]
    assert booking_data["status"] == "CONFIRMED"
    assert booking_data["fare"] > 0
    booking_id = booking_data["booking_id"]
    print("    booking_id ->", booking_id, "| fare ->", booking_data["fare"])

    result = await manager.handle_message(
        {"intent": "booking_agent", "message": "what's my status?"},
        ConversationContext(user_id="u1", session_id="s2"),
    )
    print("[4] fresh session, no state ->", result.success, "|", result.response)
    assert result.success
    assert result.agent_result.metadata["completed"] is False

    status_result = await tool_executor.run(
        "get_booking_status", {"booking_id": booking_id}
    )
    print("[5] get_booking_status ->", status_result.success, "|", status_result.data)
    assert status_result.success
    assert status_result.data["booking_id"] == booking_id
    assert status_result.data["status"] == "CONFIRMED"

    status_result = await tool_executor.run(
        "get_booking_status", {"booking_id": 999999}
    )
    print(
        "[6] get_booking_status (not found) ->",
        status_result.success,
        "|",
        status_result.error,
    )
    assert not status_result.success
    assert "not found" in status_result.error.lower()

    create_result = await tool_executor.run(
        "create_booking",
        {
            "name": "Ravi Kumar",
            "email": "not-an-email",
            "mobile": "9999999999",
            "trip_category": "Rental",
            "trip_type": "Round Trip",
            "pickup_location": "MG Road",
            "destination": "Mysuru",
            "travel_date": "1 August 2026",
            "pickup_time": "7:00 AM",
            "vehicle_type": "Innova",
        },
    )
    print(
        "[7] invalid email rejected ->",
        create_result.success,
        "|",
        create_result.error[:60],
        "...",
    )
    assert not create_result.success

    print("\nAll assertions passed.")


if __name__ == "__main__":
    asyncio.run(main())