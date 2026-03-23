from core.rag.embeddings import EmbeddingModel
from core.rag.vector_store import VectorStore


class Retriever:
    """
    Semantic retriever for products.
    """

    def __init__(self):
        self.embedder = EmbeddingModel()
        self.store = VectorStore(dim=384)

    def index_products(self, products: list[dict]):
        texts = [
            f"{p['title']} {p.get('platform')} {p.get('price')} INR"
            for p in products
        ]
        vectors = self.embedder.embed(texts)
        self.store.add(vectors, products)

    def find_similar(self, query: str, k: int = 10):
        vector = self.embedder.embed([query])
        return self.store.search(vector, k)
