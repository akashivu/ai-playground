from langchain_core.prompts import (ChatPromptTemplate,MessagesPlaceholder,)

from langchain_core.messages import (HumanMessage,AIMessage,)

from langchain_core.output_parsers import (
    StrOutputParser,)

from config.llm_config import (get_llm,)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a senior Spring Security engineer.
Provide concise answers.
""",),

        MessagesPlaceholder(variable_name="history",),("human","{question}",),])

chain = (
    prompt
    | get_llm(temperature=0)
    | StrOutputParser())

result = chain.invoke(
    {
        "history": [
            HumanMessage(
                content="What is JWT?"
            ),

            AIMessage(
                content="JWT is a token-based authentication mechanism."
            ),
        ],

        "question":
        "How does it work?",})

print(result)