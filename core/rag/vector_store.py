import faiss
import numpy as np
import os
import pickle


class VectorStore:
    """
    FAISS-based vector store with disk persistence.
    """

    def __init__(self, dim: int, index_path="local_memory/faiss_index.index", data_path="local_memory/faiss_index.pkl"):
        self.dim = dim
        self.index_path = index_path
        self.data_path = data_path

        os.makedirs(os.path.dirname(index_path), exist_ok=True)

        if os.path.exists(index_path) and os.path.exists(data_path):
            self.index = faiss.read_index(index_path)
            with open(data_path, "rb") as f:
                self.data = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.data = []

    def add(self, vectors: np.ndarray, metadata: list[dict]):
        self.index.add(vectors)
        self.data.extend(metadata)
        self._persist()

    def search(self, query_vector: np.ndarray, k: int = 10):
        if self.index.ntotal == 0:
            return []

        distances, indices = self.index.search(query_vector, k)

        SIMILARITY_THRESHOLD = 0.8  # tune if needed

        seen = set()
        results = []

        for dist, i in zip(distances[0], indices[0]):
            if i == -1:
                continue

            # Drop weak matches
            if dist > SIMILARITY_THRESHOLD:
                continue

            if i < len(self.data):
                item_id = id(self.data[i])
                if item_id not in seen:
                    seen.add(item_id)
                    results.append(self.data[i])

        return results


    def _persist(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.data_path, "wb") as f:
            pickle.dump(self.data, f)
