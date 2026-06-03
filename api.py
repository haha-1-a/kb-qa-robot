"""FastAPI 后端 — 提供 RESTful API 供移动端和远程调用"""
import os
import tempfile
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import Config
from core.document_loader import load_document
from core.embedding_client import EmbeddingClient
from core.llm_client import DeepSeekClient
from core.retriever import Retriever
from core.text_splitter import split_documents
from core.vector_store import VectorStore
from utils.helpers import ensure_dirs, save_uploaded_file


# ── 生命周期 ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_dirs()
    yield


app = FastAPI(
    title="企业知识库问答机器人 API",
    description="基于 RAG 架构的知识库智能问答系统",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 模型 ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str
    top_k: int = Config.DEFAULT_TOP_K
    temperature: float = Config.DEFAULT_TEMPERATURE
    model: str = Config.DEFAULT_MODEL
    history: List[dict] = []


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict] = []


class SearchRequest(BaseModel):
    query: str
    top_k: int = Config.DEFAULT_TOP_K


class SearchResponse(BaseModel):
    results: List[dict]


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    db_size_mb: float


# ── 依赖 ──────────────────────────────────────────────────
_vs: Optional[VectorStore] = None
_ec: Optional[EmbeddingClient] = None


def get_vs() -> VectorStore:
    global _vs
    if _vs is None:
        _vs = VectorStore()
    return _vs


def get_ec() -> EmbeddingClient:
    global _ec
    if _ec is None:
        _ec = EmbeddingClient(api_type=Config.EMBEDDING_API_TYPE)
    return _ec


def get_retriever() -> Retriever:
    return Retriever(get_vs(), get_ec())


# ── 路由 ──────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """RAG 问答"""
    try:
        retriever = get_retriever()
        contexts = retriever.retrieve(req.question, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(500, f"检索失败: {e}")

    if not contexts or all(c[2] < 0.1 for c in contexts):
        return ChatResponse(
            answer="抱歉，知识库中暂无相关内容。请尝试上传相关文档后再提问。",
            sources=[],
        )

    try:
        llm = DeepSeekClient(model=req.model, temperature=req.temperature)
        answer = llm.answer_with_context(req.question, contexts, req.history)
    except Exception as e:
        raise HTTPException(500, f"LLM 调用失败: {e}")

    sources = [
        {"source": c[1].get("source", "unknown"), "score": round(c[2], 4), "text": c[0][:300]}
        for c in contexts
    ]
    return ChatResponse(answer=answer, sources=sources)


@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    """语义检索（不生成回答，仅返回相关片段）"""
    try:
        retriever = get_retriever()
        contexts = retriever.retrieve(req.query, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(500, f"检索失败: {e}")

    results = [
        {
            "text": c[0],
            "source": c[1].get("source", "unknown"),
            "score": round(c[2], 4),
        }
        for c in contexts
    ]
    return SearchResponse(results=results)


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    """上传文档到知识库"""
    vs = get_vs()
    ec = get_ec()
    success = []
    failed = []

    for uf in files:
        try:
            # FastAPI UploadFile 使用 filename 属性
            fname = uf.filename
            file_path = os.path.join(Config.DOCUMENTS_DIR, fname)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            content = await uf.read()
            with open(file_path, "wb") as f:
                f.write(content)
            docs = load_document(file_path)
            if not docs:
                raise ValueError("未能解析出任何内容")
            chunks = split_documents(docs)
            texts = [c.page_content for c in chunks]
            embeddings = ec.embed(texts)
            ids = [
                f"{os.path.splitext(fname)[0]}_{i}"
                for i in range(len(chunks))
            ]
            metadatas = [
                {"source": fname, "type": os.path.splitext(fname)[1], "chunk_index": i}
                for i in range(len(chunks))
            ]
            vs.add_documents(texts, embeddings, metadatas, ids)
            success.append(fname)
        except Exception as e:
            failed.append({"file": fname, "error": str(e)[:100]})

    return {"success": success, "failed": failed}


@app.get("/stats", response_model=StatsResponse)
async def stats():
    """知识库统计"""
    s = get_vs().get_stats()
    return StatsResponse(**s)


@app.get("/documents")
async def documents():
    """文档列表"""
    return get_vs().get_all_documents()


@app.delete("/documents/{source:path}")
async def delete_document(source: str):
    """删除指定文档"""
    from urllib.parse import unquote
    source = unquote(source)
    get_vs().delete_by_source(source)
    return {"deleted": source}


@app.delete("/collection")
async def clear_collection():
    """清空知识库"""
    get_vs().delete_collection()
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
