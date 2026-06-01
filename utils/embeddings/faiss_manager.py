import faiss
import numpy as np
import pickle
from typing import List

class FaissManager:
    def __init__(self, dim: int = 1536, index_path: str = "data/knowledge.index"):
        self.index_path = index_path
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)

    def add_embeddings(self, vectors: List[np.ndarray]):
        self.index.add(np.array(vectors, dtype=np.float32))

    def search(self, query_vector: np.ndarray, top_k: int = 3):
        D, I = self.index.search(np.array([query_vector], dtype=np.float32), top_k)
        return I[0], D[0]

    def save(self):
        faiss.write_index(self.index, self.index_path)

    def load(self):
        self.index = faiss.read_index(self.index_path)
