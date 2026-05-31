import time
from typing import List

import requests
from openai import OpenAI

from config import Config


class EmbeddingClient:
    """支持本地模型、OpenAI 和阿里云 DashScope 的 Embedding 客户端"""

    def __init__(self, api_type: str = None):
        self.api_type = api_type or Config.EMBEDDING_API_TYPE
        if self.api_type == "local":
            self._init_local()
        elif self.api_type == "openai":
            self._init_openai()
        elif self.api_type == "dashscope":
            self._init_dashscope()
        else:
            raise ValueError(f"不支持的 Embedding API 类型: {self.api_type}")

    def _init_local(self):
        from sentence_transformers import SentenceTransformer
        self.model = Config.LOCAL_EMBEDDING_MODEL
        self._st_model = SentenceTransformer(self.model)

    def _init_openai(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("未设置 OPENAI_API_KEY")
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_EMBEDDING_MODEL

    def _init_dashscope(self):
        if not Config.DASHSCOPE_API_KEY:
            raise ValueError("未设置 DASHSCOPE_API_KEY")
        self.api_key = Config.DASHSCOPE_API_KEY
        self.model = Config.DASHSCOPE_EMBEDDING_MODEL

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self.api_type == "local":
            return self._embed_local(texts)
        elif self.api_type == "openai":
            return self._embed_openai(texts)
        else:
            return self._embed_dashscope(texts)

    def _embed_local(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._st_model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in resp.data]

    def _embed_dashscope(self, texts: List[str]) -> List[List[float]]:
        url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        results = []
        for text in texts:
            payload = {
                "model": self.model,
                "input": {"texts": [text]},
            }
            resp = requests.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"DashScope API 错误: {resp.text}")
            data = resp.json()
            results.append(data["output"]["embeddings"][0]["embedding"])
            time.sleep(0.05)
        return results

    def embed_query(self, text: str) -> List[float]:
        embeddings = self.embed([text])
        return embeddings[0] if embeddings else []
