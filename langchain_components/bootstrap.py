"""
Import this once at app startup. Registers all agents (and their
planners/tools, since each agent already imports those itself).

Just imports, nothing else.
"""

import langchain_components.agents.booking_agent
import langchain_components.agents.itinerary_agent
