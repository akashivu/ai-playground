from langchain_components.routing.intent_classifier_prompt import intent_classifier_prompt
from langchain_components.routing.intent_classifier_parser import intent_classifier_parser
from config.llm_config import get_llm
from langchain_core.runnables import RunnableLambda


def _get_chain():
    return intent_classifier_prompt | get_llm(temperature=0) | intent_classifier_parser


intent_classifier_chain = RunnableLambda(lambda x: _get_chain().invoke(x))
