class ContextMemory:
    """
    Manages conversational context for the AI engine.
    """

    def __init__(self, store):
        self.store = store

    def save_product(self, product: dict):
        self.store.set("last_product", product)

    def get_last_product(self):
        return self.store.get("last_product")
