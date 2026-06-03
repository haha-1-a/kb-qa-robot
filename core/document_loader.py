import os
import tempfile
from typing import List

import docx2txt
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from core.multimodal_processor import load_image_as_document, load_video_as_document


def load_pdf(file_path: str) -> List[Document]:
    loader = PyPDFLoader(file_path)
    return loader.load()


def load_docx(file_path: str) -> List[Document]:
    text = docx2txt.process(file_path)
    if not text or not text.strip():
        return []
    return [Document(page_content=text, metadata={"source": os.path.basename(file_path)})]


def load_md(file_path: str) -> List[Document]:
    return _load_text_file(file_path)


def load_txt(file_path: str) -> List[Document]:
    return _load_text_file(file_path)


def _load_text_file(file_path: str) -> List[Document]:
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = os.path.basename(file_path)
    return docs


def load_xlsx(file_path: str) -> List[Document]:
    try:
        xls = pd.ExcelFile(file_path)
        docs = []
        source_name = os.path.basename(file_path)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            text = df.to_string(index=False)
            if text.strip():
                docs.append(Document(
                    page_content=text,
                    metadata={"source": source_name, "sheet": sheet_name}
                ))
        return docs
    except Exception:
        df = pd.read_excel(file_path)
        text = df.to_string(index=False)
        return [Document(page_content=text, metadata={"source": os.path.basename(file_path)})]


def load_image(file_path: str) -> List[Document]:
    doc = load_image_as_document(file_path)
    return [doc] if doc else []


def load_video(file_path: str) -> List[Document]:
    doc = load_video_as_document(file_path)
    return [doc] if doc else []


LOADERS = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".md": load_md,
    ".txt": load_txt,
    ".xlsx": load_xlsx,
    ".jpg": load_image,
    ".jpeg": load_image,
    ".png": load_image,
    ".mp4": load_video,
}


def load_document(file_path: str) -> List[Document]:
    ext = os.path.splitext(file_path)[1].lower()
    loader = LOADERS.get(ext)
    if not loader:
        raise ValueError(f"不支持的文档格式: {ext}")
    return loader(file_path)


def load_folder(folder_path: str) -> List[Document]:
    all_docs = []
    for root, _, files in os.walk(folder_path):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in LOADERS:
                try:
                    docs = load_document(os.path.join(root, fname))
                    all_docs.extend(docs)
                except Exception as e:
                    print(f"加载文件失败 {fname}: {e}")
    return all_docs
