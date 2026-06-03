import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # DeepSeek
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

    # Embedding
    EMBEDDING_API_TYPE = os.getenv("EMBEDDING_API_TYPE", "local")
    LOCAL_EMBEDDING_MODEL = os.getenv("LOCAL_EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_EMBEDDING_MODEL = "text-embedding-v2"

    # Chroma
    CHROMA_PERSIST_PATH = "./data/chroma_db"
    CHROMA_COLLECTION_NAME = "kb_documents"

    # Text splitting
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50

    # Retrieval
    DEFAULT_TOP_K = 4
    MAX_TOP_K = 10

    # Data paths
    DOCUMENTS_DIR = "./data/documents"
    HISTORY_PATH = "./data/history.json"

    # Default LLM settings
    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_TEMPERATURE = 0.7

    # Vision model
    VISION_MODEL = os.getenv("VISION_MODEL", "deepseek-chat")
    VISION_MAX_TOKENS = int(os.getenv("VISION_MAX_TOKENS", "1024"))

    # API service
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Streamlit service
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
