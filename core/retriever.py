from typing import List, Tuple

from core.embedding_client import EmbeddingClient
from core.vector_store import VectorStore


class Retriever:
    def __init__(self, vector_store: VectorStore, embedding_client: EmbeddingClient):
        self.vector_store = vector_store
        self.embedding_client = embedding_client

    def retrieve(self, query: str, top_k: int = 4) -> List[Tuple[str, dict, float]]:
        """检索相关片段，返回 [(text, metadata, score), ...]"""
        query_embedding = self.embedding_client.embed_query(query)
        if not query_embedding:
            return []

        results = self.vector_store.search(query_embedding, top_k=top_k)

        contexts = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i, text in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            distance = distances[i] if i < len(distances) else 0
            # Chroma 返回的是距离，cosine 距离转相似度
            score = 1 - distance
            contexts.append((text, meta, max(0, score)))

        return contexts
