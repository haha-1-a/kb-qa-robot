import hashlib
import os
import shutil
from typing import List

from config import Config


def ensure_dirs():
    os.makedirs(Config.DOCUMENTS_DIR, exist_ok=True)
    os.makedirs(Config.CHROMA_PERSIST_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(Config.HISTORY_PATH), exist_ok=True)


def get_file_hash(file_path: str) -> str:
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def save_uploaded_file(uploaded_file, target_dir: str = None) -> str:
    """保存上传的文件，返回保存路径"""
    target_dir = target_dir or Config.DOCUMENTS_DIR
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def format_file_size(size_bytes: float) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def get_supported_extensions() -> List[str]:
    return [".pdf", ".docx", ".md", ".txt", ".xlsx"]
