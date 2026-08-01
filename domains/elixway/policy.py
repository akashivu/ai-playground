from langchain_components.guardrails.domain_policy import DomainPolicy

ELIXWAY_POLICY = DomainPolicy(
    domain_name="elixway",
    allowed_topics=[
        "travel", "tourism", "transportation",
        "vehicle_booking", "trip_planning", "pricing", "destinations",
    ],
    restricted_capabilities=[
        "code_generation", "essay_writing", "resume_creation", "general_tutoring",
    ],
    refusal_message=(
        "I'm Elixway AI Assistant and can only help with travel "
        "packages, bookings, pricing, and destinations. How can I help with your trip?"
    ),
)