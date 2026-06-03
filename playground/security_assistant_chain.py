from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.llm_config import get_llm

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior Spring Security engineer. Provide concise and accurate answers."),
    ("human", "Question:\n{question}"),
])

chain = prompt | get_llm(temperature=0) | StrOutputParser()

result = chain.invoke({"question": "What is JWT authentication?"})
print(result)