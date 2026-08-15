"""
Prompt for an LLM-based QueryRewriter (see query_rewriter.py's
`QueryRewriter` protocol). Not called by the default template-based
implementation — useful for queries whose intent is clear but which
don't match any fixed rewrite template.
"""

REWRITE_SYSTEM_PROMPT = """Rewrite the user's conversational query into a \
short, keyword-dense phrase optimized for retrieval against a knowledge \
base of FAQs, policies, pricing, vehicles, and city information.

Examples:
"Can I bring my dog?" -> "pet travel policy"
"Do I get refund?" -> "refund cancellation policy"
"Need tempo" -> "tempo traveller vehicle specification"

Respond with ONLY the rewritten phrase, no other text.
"""


def build_rewrite_prompt(query: str, intent: str, entities: list[str]) -> str:
    return (
        f"{REWRITE_SYSTEM_PROMPT}\n\n"
        f"Query: {query!r}\nIntent: {intent}\nEntities: {entities}"
    )
