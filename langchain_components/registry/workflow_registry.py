from typing import Callable

from langchain_components.routing.intent_types import IntentType

from langchain_components.workflows.general_chat_workflow import (
    general_chat_workflow,
)

from langchain_components.workflows.booking_workflow import (
    booking_workflow,
)

from langchain_components.workflows.booking_status_workflow import (
    booking_status_workflow,
)

from langchain_components.workflows.recommendation_workflow import (
    recommendation_workflow,
)

from langchain_components.workflows.destination_info_workflow import (
    destination_info_workflow,
)

from langchain_components.workflows.knowledge_search_workflow import (
    knowledge_search_workflow,
)

from langchain_components.workflows.faq_workflow import (
    faq_workflow,
)

from langchain_components.workflows.pricing_workflow import (
    pricing_workflow,
)

from langchain_components.workflows.policy_workflow import (
    policy_workflow,
)

from langchain_components.workflows.out_of_domain_workflow import (
    out_of_domain_workflow,
)

from langchain_components.workflows.itinerary_workflow import (
    itinerary_workflow,
)

from langchain_components.workflows.flight_search_workflow import (
    flight_search_workflow,
)


WORKFLOWS: dict[IntentType, Callable] = {
    IntentType.GENERAL: general_chat_workflow,

    IntentType.BOOKING: booking_workflow,

    IntentType.BOOKING_STATUS: booking_status_workflow,

    IntentType.RECOMMENDATION: recommendation_workflow,

    
    IntentType.DESTINATION_INFO: destination_info_workflow,

    IntentType.KNOWLEDGE_SEARCH: knowledge_search_workflow,

    IntentType.FAQ: faq_workflow,

    IntentType.PRICING: pricing_workflow,

    IntentType.POLICY: policy_workflow,

    IntentType.OUT_OF_DOMAIN: out_of_domain_workflow,

    IntentType.ITINERARY: itinerary_workflow,

    IntentType.FLIGHT_SEARCH: flight_search_workflow,
}