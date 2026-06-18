from langchain_components.guardrails.domain_policy import DomainPolicy

ADIYOGICABZ_POLICY = DomainPolicy(
    domain_name="adiyogicabz",
    allowed_topics=[
        "travel", "tourism", "transportation",
        "vehicle_booking", "trip_planning", "pricing", "destinations",
    ],
    restricted_capabilities=[
        "code_generation", "essay_writing", "resume_creation", "general_tutoring",
    ],
    refusal_message=(
        "I'm AdiyogiCabz AI Assistant and can only help with travel "
        "packages, bookings, pricing, and destinations. How can I help with your trip?"
    ),
)