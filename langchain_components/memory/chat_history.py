from langchain_core.chat_history import ( InMemoryChatMessageHistory,)

def get_chat_history():
    """return inmemory chat history instances"""

    return InMemoryChatMessageHistory()