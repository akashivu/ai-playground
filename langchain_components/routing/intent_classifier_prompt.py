from langchain_core.prompts import PromptTemplate

from langchain_components.routing.intent_types import IntentType


INTENT_DEFINITIONS = (
    "FAQ: Informational questions about how Elixway works, how to use features, "
    "booking capabilities, procedures, or common customer questions.\n"

    "POLICY: Questions about company policies, rules, cancellation, refunds, "
    "rescheduling, payments, waiting charges, luggage, driver rules, tolls, privacy, "
    "terms, booking rules, and other policy-specific requirements.\n"

    "KNOWLEDGE_SEARCH: Questions requiring retrieval from documents, guides, "
    "or the Elixway knowledge base where the answer is primarily informational "
    "and not better classified as a specific policy, pricing, booking, itinerary, "
    "recommendation, or flight-search request.\n"

    "BOOKING: Explicit requests to perform or start a booking action, such as "
    "booking, reserving, scheduling, or arranging a ride/service.\n"

    "BOOKING_STATUS: Questions asking about the current status, progress, confirmation, "
    "driver assignment, or state of an existing booking.\n"

    "RECOMMENDATION: Requests for recommendations or suggestions when the user "
    "needs help choosing a destination, place, vacation idea, vehicle, or travel option. "
    "This includes questions about where to travel, where to go, which destination "
    "to choose, what place to visit, or what type of trip to consider. "
    "The user does not need to explicitly use words such as 'recommend' or 'suggest'.\n"

    "PRICING: Questions about price, fare, cost, rates, charges, surcharges, "
    "or other trip/service pricing.\n"

    "ITINERARY: Requests to create a structured trip plan, day-wise itinerary, "
    "travel schedule, activities, or places to visit when the destination is already "
    "known or explicitly provided. If the user is asking the assistant to choose "
    "the destination or place, use RECOMMENDATION instead.\n"

    "GENERAL: Greetings, casual conversation, or simple travel-related questions "
    "that do not fit another intent.\n"

    "OUT_OF_DOMAIN: Requests unrelated to Elixway travel, bookings, pricing, "
    "or supported travel assistance, including coding, writing, tutoring, or "
    "general knowledge.\n"

    "FLIGHT_SEARCH: Requests to search for flights between an origin and destination.\n"
)


EXAMPLES = (
    "Examples:\n"

    # ---------------------------------------------------------
    # FAQ
    # ---------------------------------------------------------

    "User: Can I book a round trip? -> FAQ\n"
    "User: How do I book a round trip? -> FAQ\n"
    "User: Is round-trip booking available? -> FAQ\n"
    "User: Can I book a ride for someone else? -> FAQ\n"
    "User: What happens after I confirm a booking? -> FAQ\n"
    "User: How far in advance can I book? -> FAQ\n"
    "User: What vehicles do you have? -> FAQ\n"
    "User: How can I share my trip status? -> FAQ\n"

    # ---------------------------------------------------------
    # BOOKING
    # ---------------------------------------------------------

    "User: Book me a round trip. -> BOOKING\n"
    "User: I want to book a round trip. -> BOOKING\n"
    "User: Book a cab from Bangalore to Goa. -> BOOKING\n"
    "User: Create a booking from Bangalore to Delhi. -> BOOKING\n"
    "User: Reserve an Innova for airport pickup. -> BOOKING\n"
    "User: Schedule a cab for tomorrow morning. -> BOOKING\n"

    # ---------------------------------------------------------
    # BOOKING STATUS
    # ---------------------------------------------------------

    "User: What is the status of my booking? -> BOOKING_STATUS\n"
    "User: Has my driver been assigned? -> BOOKING_STATUS\n"
    "User: Is my booking confirmed? -> BOOKING_STATUS\n"
    "User: Where is my driver? -> BOOKING_STATUS\n"

    # ---------------------------------------------------------
    # FLIGHT SEARCH
    # ---------------------------------------------------------

    "User: Find flights from Mumbai to Dubai. -> FLIGHT_SEARCH\n"
    "User: Search flights from Delhi to Bangkok on 2026-09-05. -> FLIGHT_SEARCH\n"
    "User: Show me flights from Bangalore to Singapore. -> FLIGHT_SEARCH\n"
    "User: What flights are available from Mumbai to Dubai? -> FLIGHT_SEARCH\n"

    # ---------------------------------------------------------
    # PRICING
    # ---------------------------------------------------------

    "User: How much is airport pickup? -> PRICING\n"
    "User: What is the fare for Mysore? -> PRICING\n"
    "User: Cab cost to Bangalore airport? -> PRICING\n"
    "User: What is the round-trip cost? -> PRICING\n"

    # ---------------------------------------------------------
    # RECOMMENDATION - VEHICLE
    # ---------------------------------------------------------

    "User: Suggest a vehicle for 8 people. -> RECOMMENDATION\n"
    "User: Which vehicle is best for 6 passengers? -> RECOMMENDATION\n"
    "User: What vehicle should I choose for a group of 7? -> RECOMMENDATION\n"

    # ---------------------------------------------------------
    # RECOMMENDATION - DESTINATION
    # ---------------------------------------------------------

    "User: Where should I travel? -> RECOMMENDATION\n"
    "User: Where should I go for my vacation? -> RECOMMENDATION\n"
    "User: Suggest a destination for me. -> RECOMMENDATION\n"
    "User: Where can I go for 5 days? -> RECOMMENDATION\n"
    "User: Which place should I visit in India? -> RECOMMENDATION\n"
    "User: I want a relaxing vacation. Where should I go? -> RECOMMENDATION\n"
    "User: Give me some travel destination ideas. -> RECOMMENDATION\n"
    "User: What are some good places to travel to? -> RECOMMENDATION\n"
    "User: I don't know where to travel. Help me choose. -> RECOMMENDATION\n"
    "User: Suggest a destination for a 3-day trip. -> RECOMMENDATION\n"
    "User: Where can I travel in December? -> RECOMMENDATION\n"
    "User: What is a good beach destination? -> RECOMMENDATION\n"
    "User: Suggest a place for a family vacation. -> RECOMMENDATION\n"

    # ---------------------------------------------------------
    # ITINERARY
    # ---------------------------------------------------------

    "User: Plan a 5-day trip to Goa. -> ITINERARY\n"
    "User: Create an itinerary for Kerala. -> ITINERARY\n"
    "User: Places to visit in Mysore for 3 days. -> ITINERARY\n"
    "User: Plan my vacation in Jaipur. -> ITINERARY\n"
    "User: What should I do in Delhi for 4 days? -> ITINERARY\n"
    "User: Create a day-wise itinerary for Mumbai. -> ITINERARY\n"

    # ---------------------------------------------------------
    # POLICY
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # GENERAL
    # ---------------------------------------------------------

    "User: Hello -> GENERAL\n"
    "User: Hi -> GENERAL\n"
    "User: Thanks -> GENERAL\n"

    # ---------------------------------------------------------
    # OUT OF DOMAIN
    # ---------------------------------------------------------

    "User: Write Python code -> OUT_OF_DOMAIN\n"
    "User: What is machine learning? -> OUT_OF_DOMAIN\n"
)


intent_classifier_prompt = PromptTemplate(
    input_variables=[
        "question",
    ],
    partial_variables={
        "valid_intents": ", ".join(
            IntentType.values()
        ),
        "intent_definitions": INTENT_DEFINITIONS,
        "examples": EXAMPLES,
    },
    template=(
        "You are the intent classifier for the Elixway travel and cab-booking platform.\n\n"

        "Your task is to classify the user's message into exactly ONE of the "
        "allowed intents.\n\n"

        "Intent definitions:\n"
        "{intent_definitions}\n\n"

        "{examples}\n"

        "============================================================\n"
        "RECOMMENDATION VS ITINERARY RULE\n"
        "============================================================\n"

        "Use RECOMMENDATION when the user wants help choosing a destination, "
        "place, vacation idea, vehicle, or travel option.\n"

        "This includes natural questions such as:\n"
        "- Where should I travel?\n"
        "- Where should I go?\n"
        "- Where can I go for 5 days?\n"
        "- Which destination should I choose?\n"
        "- Suggest a place for my vacation.\n"
        "- What are some good places to visit?\n"
        "- I want a beach vacation. Where should I go?\n\n"

        "The user does NOT need to explicitly say 'recommend' or 'suggest'. "
        "A question asking the assistant to choose a destination or travel option "
        "is still RECOMMENDATION.\n\n"

        "Use ITINERARY when the destination is already known and the user wants "
        "a structured plan, schedule, activities, or day-wise itinerary.\n\n"

        "Examples:\n"
        "- 'Where should I travel?' -> RECOMMENDATION\n"
        "- 'Suggest a destination for 5 days.' -> RECOMMENDATION\n"
        "- 'Which place should I visit in India?' -> RECOMMENDATION\n"
        "- 'Plan 5 days in Goa.' -> ITINERARY\n"
        "- 'Create an itinerary for Kerala.' -> ITINERARY\n"
        "- 'What should I do in Jaipur for 3 days?' -> ITINERARY\n\n"

        "============================================================\n"
        "CRITICAL BOOKING VS FAQ RULE\n"
        "============================================================\n"

        "The presence of the word 'book' does NOT automatically mean BOOKING.\n\n"

        "BOOKING is only for an explicit request to perform or start a booking action.\n"

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

        "============================================================\n"
        "FLIGHT SEARCH RULE\n"
        "============================================================\n"

        "Use FLIGHT_SEARCH when the user wants to search for or find available "
        "flights between an origin and destination.\n\n"

        "Examples:\n"
        "- 'Find flights from Mumbai to Dubai.' -> FLIGHT_SEARCH\n"
        "- 'Search flights from Delhi to Bangkok.' -> FLIGHT_SEARCH\n"
        "- 'What flights are available from Mumbai to Dubai?' -> FLIGHT_SEARCH\n\n"

        "============================================================\n"
        "GENERAL DECISION RULES\n"
        "============================================================\n"

        "1. Determine what the user is primarily trying to accomplish.\n"
        "2. Choose the most specific intent that matches the user's goal.\n"
        "3. If the user wants the assistant to choose a destination or travel option, "
        "use RECOMMENDATION.\n"
        "4. If the destination is already known and the user wants a detailed plan, "
        "use ITINERARY.\n"
        "5. If the user explicitly asks the assistant to perform a booking action, "
        "use BOOKING.\n"
        "6. If the user asks whether booking is possible, how it works, or what "
        "booking options exist, use FAQ.\n"
        "7. Do not classify based only on isolated keywords. Consider the meaning "
        "of the complete user message.\n"
        "8. Never classify a question as BOOKING solely because it contains "
        "the words 'book', 'booking', 'ride', or 'cab'.\n"
        "9. Choose exactly one intent.\n\n"

        "Valid intents:\n"
        "{valid_intents}\n\n"

        "Question:\n"
        "{question}\n\n"

        "Respond ONLY with valid JSON using exactly this structure:\n"
        '{{"intent":"<VALID_INTENT>"}}'
    ),
)