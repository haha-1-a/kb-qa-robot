import os
import tempfile
import time
from datetime import datetime

import streamlit as st

from config import Config
from core.document_loader import load_document, load_folder
from core.embedding_client import EmbeddingClient
from core.llm_client import DeepSeekClient
from core.retriever import Retriever
from core.text_splitter import split_documents
from core.vector_store import VectorStore
from utils.helpers import ensure_dirs, save_uploaded_file
from utils.history_manager import HistoryManager

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(
    page_title="企业知识库问答机器人",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_dirs()

# ── 初始化 session state ──────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # 当前对话轮次
if "history_manager" not in st.session_state:
    st.session_state.history_manager = HistoryManager(Config.HISTORY_PATH)
if "top_k" not in st.session_state:
    st.session_state.top_k = Config.DEFAULT_TOP_K
if "temperature" not in st.session_state:
    st.session_state.temperature = Config.DEFAULT_TEMPERATURE
if "model_name" not in st.session_state:
    st.session_state.model_name = Config.DEFAULT_MODEL
if "embedding_api_type" not in st.session_state:
    st.session_state.embedding_api_type = Config.EMBEDDING_API_TYPE
if "pending_ask" not in st.session_state:
    st.session_state.pending_ask = None


# ── 懒加载客户端 ──────────────────────────────────────────
@st.cache_resource
def get_vector_store():
    return VectorStore()


@st.cache_resource
def get_embedding_client(api_type):
    return EmbeddingClient(api_type=api_type)


def get_llm_client():
    return DeepSeekClient(
        model=st.session_state.model_name,
        temperature=st.session_state.temperature,
    )


def check_api_config():
    """检查 API 配置是否就绪，返回 (ok, message)"""
    issues = []
    if not Config.DEEPSEEK_API_KEY or Config.DEEPSEEK_API_KEY.startswith("sk-xxx"):
        issues.append("DeepSeek API Key")
    api_type = st.session_state.get("embedding_api_type", Config.EMBEDDING_API_TYPE)
    if api_type == "local":
        pass  # 本地模型无需 API Key
    elif api_type == "openai":
        if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY.startswith("sk-xxx"):
            issues.append("OpenAI API Key (Embedding)")
    elif api_type == "dashscope":
        if not Config.DASHSCOPE_API_KEY or Config.DASHSCOPE_API_KEY.startswith("sk-xxx"):
            issues.append("DashScope API Key (Embedding)")
    if issues:
        return False, f"请先在 .env 文件中配置: {', '.join(issues)}"
    return True, "OK"


def get_retriever():
    vs = get_vector_store()
    ec = get_embedding_client(st.session_state.embedding_api_type)
    return Retriever(vs, ec)


# ── 标题 ──────────────────────────────────────────────────
st.title("📚 企业知识库问答机器人")

# ── 侧边栏 ────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 设置")

    st.subheader("API 配置")
    api_ok, api_msg = check_api_config()
    if api_ok:
        st.success("API 配置就绪")
    else:
        st.warning(api_msg)

    st.session_state.embedding_api_type = st.selectbox(
        "Embedding API",
        options=["local", "openai", "dashscope"],
        index=0 if st.session_state.embedding_api_type not in ("openai", "dashscope")
        else (1 if st.session_state.embedding_api_type == "openai" else 2),
        help="local: 本地免费模型 / openai: OpenAI / dashscope: 阿里云",
    )

    st.subheader("检索设置")
    st.session_state.top_k = st.slider(
        "检索数量 Top-K",
        min_value=1,
        max_value=10,
        value=st.session_state.top_k,
        help="每次检索返回的相关片段数量",
    )

    st.subheader("模型设置")
    st.session_state.temperature = st.slider(
        "温度参数",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1,
        help="越低回答越确定，越高越有创造性",
    )
    st.session_state.model_name = st.selectbox(
        "LLM 模型",
        options=["deepseek-chat", "deepseek-coder"],
        index=0 if st.session_state.model_name == "deepseek-chat" else 1,
        help="选择用于生成回答的模型",
    )

    st.divider()

    # ── 历史记录 ──
    st.subheader("📜 历史记录")
    hm = st.session_state.history_manager
    records = hm.get_records()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 导出 CSV", use_container_width=True):
            csv_path = os.path.join(tempfile.gettempdir(), "qa_history.csv")
            hm.export_to_csv(csv_path)
            with open(csv_path, "rb") as f:
                st.download_button(
                    "下载 CSV",
                    data=f,
                    file_name="qa_history.csv",
                    mime="text/csv",
                )
    with col2:
        if st.button("🗑️ 清空历史", use_container_width=True):
            hm.clear()
            st.rerun()

    st.caption(f"共 {len(records)} 条记录")

    for i, record in enumerate(records):
        ts = record.get("timestamp", "")[:16]
        q = record.get("question", "")
        with st.expander(f"{ts} - {q[:20]}{'...' if len(q) > 20 else ''}", expanded=False):
            st.caption(f"**问：** {record['question']}")
            st.caption(f"**答：** {record['answer'][:300]}")
            srcs = record.get("sources", [])
            if srcs:
                st.caption("**来源：**")
                for src in srcs:
                    st.caption(f"  • {src['source']} ({src['score']:.2f})")


# ── 主区域 ────────────────────────────────────────────────
tab1, tab2 = st.tabs(["💬 问答", "📁 知识库管理"])

# ═══════════════════ 问答 Tab ═══════════════════
with tab1:
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📎 引用来源"):
                        for j, src in enumerate(msg["sources"], 1):
                            st.caption(
                                f"{j}. **{src['source']}** (相关度 {src['score']:.2f})"
                            )
                            st.caption(f"> {src['text'][:300]}")

    # 输入框
    user_input = st.chat_input("💬 输入问题...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("正在检索知识库..."):
                try:
                    retriever = get_retriever()
                    contexts = retriever.retrieve(user_input, top_k=st.session_state.top_k)
                except Exception as e:
                    st.error(f"检索失败: {e}")
                    contexts = []

            if not contexts or all(c[2] < 0.1 for c in contexts):
                answer = "抱歉，知识库中暂无相关内容。请尝试上传相关文档后再提问。"
                sources = []
            else:
                with st.spinner("AI 正在生成回答..."):
                    try:
                        llm = get_llm_client()
                        history_messages = []
                        for msg in st.session_state.chat_history[-10:-1]:
                            history_messages.append({"role": msg["role"], "content": msg["content"]})
                        answer = llm.answer_with_context(user_input, contexts, history_messages)
                    except Exception as e:
                        st.error(f"调用 LLM 失败: {e}")
                        answer = f"生成回答时出错: {e}"
                    sources = [
                        {"source": c[1].get("source", "unknown"), "score": c[2], "text": c[0]}
                        for c in contexts
                    ]

            st.markdown(answer)
            if sources:
                with st.expander("📎 引用来源"):
                    for j, src in enumerate(sources, 1):
                        st.caption(f"{j}. **{src['source']}** (相关度 {src['score']:.2f})")
                        st.caption(f"> {src['text'][:300]}")

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
            })

            # 保存历史
            st.session_state.history_manager.add_record(user_input, answer, contexts)

            st.rerun()

# ═══════════════════ 知识库管理 Tab ═══════════════════
with tab2:
    vs = get_vector_store()

    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_files = st.file_uploader(
            "📁 上传文件",
            type=["pdf", "docx", "md", "txt", "xlsx"],
            accept_multiple_files=True,
            key="file_uploader",
            help="选择一个或多个文档文件上传",
        )

    with col2:
        col_folder_input, col_clear = st.columns([3, 1])
        with col_folder_input:
            folder_path = st.text_input(
                "📂 本地文件夹路径",
                placeholder="例如: D:\\公司文档",
                key="folder_path_input",
                help="输入文件夹路径后点击右侧按钮导入",
            )
        with col_clear:
            st.write("")
            if st.button("📥", use_container_width=True, help="导入该文件夹下所有支持的文档"):
                if folder_path and os.path.isdir(folder_path):
                    st.session_state.pending_folder = folder_path
                else:
                    st.error("请输入有效的文件夹路径")

        if st.button("🗑️ 清空知识库", use_container_width=True, type="secondary"):
            vs.delete_collection()
            st.success("知识库已清空")
            time.sleep(0.5)
            st.rerun()

    # ── 处理上传的文件 ──
    if uploaded_files:
        ec = get_embedding_client(st.session_state.embedding_api_type)
        progress_bar = st.progress(0)
        status_text = st.empty()
        success_count = 0
        fail_count = 0

        for i, uf in enumerate(uploaded_files):
            status_text.text(f"正在处理: {uf.name} ({i+1}/{len(uploaded_files)})")
            try:
                file_path = save_uploaded_file(uf)
                docs = load_document(file_path)
                if not docs:
                    raise ValueError("未能解析出任何内容")
                chunks = split_documents(docs)
                texts = [chunk.page_content for chunk in chunks]
                embeddings = ec.embed(texts)
                ids = [
                    f"{os.path.splitext(uf.name)[0]}_{i*1000 + j}"
                    for j in range(len(chunks))
                ]
                metadatas = [
                    {"source": uf.name, "type": os.path.splitext(uf.name)[1], "chunk_index": j}
                    for j in range(len(chunks))
                ]
                vs.add_documents(texts, embeddings, metadatas, ids)
                success_count += 1
            except Exception as e:
                fail_count += 1
                st.toast(f"处理失败: {uf.name} - {str(e)[:80]}")

            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.text(f"处理完成！成功 {success_count} 个，失败 {fail_count} 个")
        time.sleep(2)
        progress_bar.empty()
        status_text.empty()
        st.rerun()

    # ── 处理文件夹导入 ──
    if st.session_state.get("pending_folder"):
        folder_path = st.session_state.pop("pending_folder")
        ec = get_embedding_client(st.session_state.embedding_api_type)
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text(f"正在扫描文件夹: {folder_path}")
        docs = load_folder(folder_path)
        if not docs:
            st.error("该文件夹下没有找到支持的文档格式")
        else:
            chunks = split_documents(docs)
            total = len(chunks)
            success_count = 0

            # 按源文件分组处理
            source_map = {}
            for chunk in chunks:
                src = chunk.metadata.get("source", "unknown")
                source_map.setdefault(src, []).append(chunk)

            for idx, (src_name, src_chunks) in enumerate(source_map.items()):
                status_text.text(f"正在处理: {src_name} ({idx+1}/{len(source_map)})")
                try:
                    texts = [c.page_content for c in src_chunks]
                    embeddings = ec.embed(texts)
                    ids = [
                        f"{os.path.splitext(src_name)[0]}_{idx*1000 + j}"
                        for j in range(len(src_chunks))
                    ]
                    metadatas = [
                        {"source": src_name, "type": os.path.splitext(src_name)[1], "chunk_index": j}
                        for j in range(len(src_chunks))
                    ]
                    vs.add_documents(texts, embeddings, metadatas, ids)
                    success_count += 1
                except Exception as e:
                    st.toast(f"处理失败: {src_name} - {str(e)[:80]}")

                progress_bar.progress((idx + 1) / len(source_map))

            status_text.text(f"文件夹导入完成！成功 {success_count} 个文件")
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
        st.rerun()

    # 文档列表
    st.divider()
    docs_list = vs.get_all_documents()

    if docs_list:
        for doc in docs_list:
            col_info, col_del = st.columns([8, 1])
            with col_info:
                st.markdown(
                    f"📄 **{doc['source']}** — {doc['count']} 个片段 — 类型: {doc.get('type', '-')}"
                )
            with col_del:
                if st.button("🗑️", key=f"del_{doc['source']}", help=f"删除 {doc['source']}"):
                    vs.delete_by_source(doc["source"])
                    st.rerun()
    else:
        st.info("知识库为空，请上传文档")

    # 统计信息
    st.divider()
    stats = vs.get_stats()
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("📄 文档数", stats["total_documents"])
    with col_stat2:
        st.metric("✂️ 切片数", stats["total_chunks"])
    with col_stat3:
        st.metric("💾 向量库大小", f"{stats['db_size_mb']} MB")

    st.caption("最后更新: 根据系统时间动态统计")
