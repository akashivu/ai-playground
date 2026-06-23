from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from config.llm_config import get_llm


def build_topic_match_chain(topics: list[str]):
    """Creates a semantic topic matcher chain for a given set of topic keys."""
    topic_list = "\n".join(f"- {topic}" for topic in topics)

    prompt = PromptTemplate(
        input_variables=["question"],
        partial_variables={"topic_list": topic_list},
        template=(
            "Match the user's question to the closest topic.\n\n"
            "Available topics:\n{topic_list}\n\n"
            "Question:\n{question}\n\n"
            "Return JSON only.\n"
            '{{"matched_key": "airport_pickup"}}\n'
            'or\n'
            '{{"matched_key": "NONE"}}'
        ),
    )

    return prompt | get_llm(temperature=0) | JsonOutputParser()