from __future__ import annotations


class MemoryError(Exception):
    pass


class MemoryNotFoundError(MemoryError):
    def __init__(self, name: str):
        super().__init__(f"Memory backend '{name}' is not registered.")
        self.name = name


class MemoryAlreadyRegisteredError(MemoryError):
    def __init__(self, name: str):
        super().__init__(f"Memory backend '{name}' is already registered.")
        self.name = name


class MemoryStorageError(MemoryError):
    def __init__(self, backend_name: str, detail: str):
        super().__init__(f"Memory backend '{backend_name}' failed to save: {detail}")
        self.backend_name = backend_name
        self.detail = detail


class MemorySearchError(MemoryError):
    def __init__(self, backend_name: str, detail: str):
        super().__init__(f"Memory backend '{backend_name}' failed to search: {detail}")
        self.backend_name = backend_name
        self.detail = detail