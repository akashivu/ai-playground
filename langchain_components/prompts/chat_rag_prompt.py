from langchain_core.prompts import ChatPromptTemplate

chat_rag_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are AdiyogiCabz AI Assistant, a travel and cab booking assistant. "
        "Answer only using the provided context. "
        "If the answer cannot be found in the context, say: "
        "'I do not have enough information.'"
    )),
    ("human", "Context:\n{context}\n\nQuestion:\n{question}"),
])
