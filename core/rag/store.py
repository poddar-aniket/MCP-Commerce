class InMemoryStore:
    """
    Simple in-memory key-value store for session context.
    """

    def __init__(self):
        self._store = {}

    def set(self, key: str, value):
        self._store[key] = value

    def get(self, key: str):
        return self._store.get(key)

    def clear(self):
        self._store.clear()
