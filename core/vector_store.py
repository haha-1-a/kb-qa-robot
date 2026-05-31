import datetime
import os
from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings

from config import Config


class VectorStore:
    def __init__(self, persist_path: str = None):
        self.persist_path = persist_path or Config.CHROMA_PERSIST_PATH
        os.makedirs(self.persist_path, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=self.persist_path,
            settings=Settings(anonymized_telemetry=False),
        )

    @property
    def collection(self):
        try:
            return self.client.get_collection(Config.CHROMA_COLLECTION_NAME)
        except Exception:
            return self.client.create_collection(
                name=Config.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: List[str],
    ):
        coll = self.collection
        coll.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

    def search(
        self, query_embedding: List[float], top_k: int = 4
    ) -> Dict:
        coll = self.collection
        results = coll.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        return results

    def delete_by_source(self, source: str):
        """删除某个源文件的所有切片"""
        coll = self.collection
        try:
            existing = coll.get(where={"source": source})
            if existing["ids"]:
                coll.delete(ids=existing["ids"])
        except Exception:
            pass

    def delete_collection(self):
        try:
            self.client.delete_collection(Config.CHROMA_COLLECTION_NAME)
        except Exception:
            pass

    def get_all_documents(self) -> List[Dict]:
        """获取所有文档概览：源文件名 + 切片数量"""
        try:
            coll = self.collection
            data = coll.get(include=["metadatas"])
        except Exception:
            return []

        source_map = {}
        for meta in data["metadatas"]:
            src = meta.get("source", "unknown")
            if src not in source_map:
                source_map[src] = {"count": 0, "source": src, "type": meta.get("type", "unknown")}
            source_map[src]["count"] += 1
        return list(source_map.values())

    def get_stats(self) -> Dict:
        try:
            coll = self.collection
            data = coll.get(include=["metadatas"])
        except Exception:
            return {"total_documents": 0, "total_chunks": 0, "db_size_mb": 0}

        source_set = set()
        for meta in data["metadatas"]:
            source_set.add(meta.get("source", "unknown"))

        db_size = 0
        if os.path.exists(self.persist_path):
            for root, _, files in os.walk(self.persist_path):
                for f in files:
                    try:
                        db_size += os.path.getsize(os.path.join(root, f))
                    except OSError:
                        pass

        return {
            "total_documents": len(source_set),
            "total_chunks": len(data.get("ids", [])),
            "db_size_mb": round(db_size / (1024 * 1024), 2),
        }
