from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Local embedding model for RAG.
    """

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts: list[str]):
        return self.model.encode(texts, convert_to_numpy=True)
