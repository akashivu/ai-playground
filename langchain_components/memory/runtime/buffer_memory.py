from langchain_core.chat_history import (InMemoryChatMessageHistory,)


class BufferMemory:

    def __init__(self,window_size: int = 10,):
        self.window_size = (window_size)
        self.history = ( InMemoryChatMessageHistory())

    def add_user_message(self,content: str,):
        self.history.add_user_message(content)

    def add_ai_message(self,content: str,):
        self.history.add_ai_message(content)

    def get_messages(self,):
        return (self.history.messages[-self.window_size :])