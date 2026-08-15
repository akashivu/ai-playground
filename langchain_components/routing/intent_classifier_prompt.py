from langchain_core.prompts import PromptTemplate
from langchain_components.routing.intent_types import IntentType


INTENT_DEFINITIONS = (
    "FAQ: Informational questions about how Elixway works, "
    "how to use features, booking capabilities, procedures, or common customer questions.\n"

    "POLICY: Questions about company policies, rules, cancellation, refunds, "
    "rescheduling, payments, waiting charges, luggage, driver rules, tolls, privacy, "
    "terms, booking rules, and other policy-specific requirements.\n"

    "KNOWLEDGE_SEARCH: Questions requiring retrieval from documents, guides, "
    "or the Elixway knowledge base where the answer is primarily informational "
    "and not better classified as a specific policy, pricing, booking, or itinerary request.\n"

    "BOOKING: Explicit requests to perform or start a booking action, such as "
    "booking, reserving, scheduling, or arranging a ride/service.\n"

    "BOOKING_STATUS: Questions asking about the current status, progress, confirmation, "
    "driver assignment, or state of an existing booking.\n"

    "RECOMMENDATION: Requests for trip suggestions, vehicle recommendations, "
    "destination recommendations, or travel planning suggestions.\n"

    "PRICING: Questions about price, fare, cost, rates, charges, surcharges, "
    "or other trip/service pricing.\n"

    "ITINERARY: Requests to create or plan a trip, day-wise itinerary, travel schedule, "
    "places to visit, or a multi-day travel plan.\n"

    "GENERAL: Greetings, casual conversation, or simple travel-related questions "
    "that do not fit another intent.\n"

    "OUT_OF_DOMAIN: Requests unrelated to Elixway travel, bookings, pricing, "
    "or supported travel assistance, including coding, writing, tutoring, or general knowledge."
)


EXAMPLES = (
    "Examples:\n"

    
    "User: Can I book a round trip? -> FAQ\n"
    "User: How do I book a round trip? -> FAQ\n"
    "User: Is round-trip booking available? -> FAQ\n"
    "User: Can I book a ride for someone else? -> FAQ\n"
    "User: What happens after I confirm a booking? -> FAQ\n"
    "User: How far in advance can I book? -> FAQ\n"

    "User: Book me a round trip. -> BOOKING\n"
    "User: I want to book a round trip. -> BOOKING\n"
    "User: Book a cab from Bangalore to Goa. -> BOOKING\n"
    "User: Create a booking from Bangalore to Delhi. -> BOOKING\n"
    "User: Reserve an Innova for airport pickup. -> BOOKING\n"
    "User: Schedule a cab for tomorrow morning. -> BOOKING\n"

    
    "User: How much is airport pickup? -> PRICING\n"
    "User: What is the fare for Mysore? -> PRICING\n"
    "User: Cab cost to Bangalore airport? -> PRICING\n"
    "User: What is the round-trip cost? -> PRICING\n"

    # ---------------------------------------------------------
    # FAQ
    # ---------------------------------------------------------
    "User: What vehicles do you have? -> FAQ\n"
    "User: How can I share my trip status? -> FAQ\n"

    
    "User: Suggest a vehicle for 8 people. -> RECOMMENDATION\n"
    "User: Suggest a 3-day trip. -> RECOMMENDATION\n"

    
    "User: Plan a 5-day trip to Goa. -> ITINERARY\n"
    "User: Create an itinerary for Kerala. -> ITINERARY\n"
    "User: Places to visit in Mysore for 3 days. -> ITINERARY\n"
    "User: Plan my vacation. -> ITINERARY\n"

    
    "User: What is your cancellation policy? -> POLICY\n"
    "User: Can I cancel my booking? -> POLICY\n"
    "User: Is there a refund? -> POLICY\n"
    "User: What happens if I cancel within 24 hours? -> POLICY\n"
    "User: What is your refund policy? -> POLICY\n"
    "User: Are toll charges included? -> POLICY\n"
    "User: Is driver allowance extra? -> POLICY\n"
    "User: What are your waiting charges? -> POLICY\n"
    "User: Can I carry pets? -> POLICY\n"
    "User: What is your luggage policy? -> POLICY\n"
    "User: What are your payment terms? -> POLICY\n"

    
    "User: Hello -> GENERAL\n"
    "User: Write Python code -> OUT_OF_DOMAIN\n"
    "User: What is machine learning? -> OUT_OF_DOMAIN"
)


intent_classifier_prompt = PromptTemplate(
    input_variables=["question"],
    partial_variables={
        "valid_intents": ", ".join(
            IntentType.values()
        ),
        "intent_definitions": INTENT_DEFINITIONS,
        "examples": EXAMPLES,
    },
    template=(
        "You are the intent classifier for the Elixway travel and cab-booking platform.\n\n"

        "Intent definitions:\n"
        "{intent_definitions}\n\n"

        "{examples}\n"

        "CRITICAL BOOKING VS FAQ RULE:\n"
        "The presence of the word 'book' does NOT automatically mean BOOKING.\n\n"

        "BOOKING is only for an explicit request to perform an action.\n"
        "Examples:\n"
        "- 'Book me a round trip.' -> BOOKING\n"
        "- 'I want to book a cab.' -> BOOKING\n"
        "- 'Create a booking from Bangalore to Goa.' -> BOOKING\n\n"

        "FAQ is for informational, capability, or procedural questions.\n"
        "Examples:\n"
        "- 'Can I book a round trip?' -> FAQ\n"
        "- 'How do I book a round trip?' -> FAQ\n"
        "- 'Is round-trip booking available?' -> FAQ\n"
        "- 'Can I book a ride for someone else?' -> FAQ\n\n"

        "Decision rule:\n"
        "1. Determine whether the user is asking the assistant to DO something "
        "or asking for INFORMATION about something.\n"
        "2. If the user asks the assistant to perform/start a booking action, use BOOKING.\n"
        "3. If the user asks whether booking is possible, how booking works, "
        "or what booking options are available, use FAQ.\n"
        "4. Never classify a question as BOOKING solely because it contains "
        "the words 'book', 'booking', or 'ride'.\n"
        "5. Choose exactly one intent.\n\n"

        "Valid intents:\n"
        "{valid_intents}\n\n"

        "Question:\n"
        "{question}\n\n"

        "Respond ONLY with valid JSON in exactly this format:\n"
        '{{"intent":"<VALID_INTENT>"}}'
    ),
)