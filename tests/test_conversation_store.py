from langchain_components.memory.conversation.conversation_store import ConversationStore


def test_add_and_get_message():
    store = ConversationStore()
    store.add_message("session1", "user", "hello")
    messages = store.get_messages("session1")
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "hello"


def test_clear_session():
    store = ConversationStore()
    store.add_message("session1", "user", "hello")
    store.clear_session("session1")
    assert store.get_messages("session1") == []


def test_session_exists():
    store = ConversationStore()
    assert not store.session_exists("ghost")
    store.add_message("session1", "user", "hello")
    assert store.session_exists("session1")


def test_multiple_sessions_isolated():
    store = ConversationStore()
    store.add_message("session1", "user", "hello")
    store.add_message("session2", "user", "world")
    assert len(store.get_messages("session1")) == 1
    assert len(store.get_messages("session2")) == 1


def test_max_messages_respected():
    store = ConversationStore()
    for i in range(15):
        store.add_message("session1", "user", f"message {i}")
    messages = store.get_messages("session1", max_messages=10)
    assert len(messages) == 10


def test_clear_nonexistent_session_does_not_raise():
    store = ConversationStore()
    store.clear_session("nonexistent")