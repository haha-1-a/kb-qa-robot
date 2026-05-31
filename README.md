# 企业知识库问答机器人

基于 RAG（检索增强生成）架构的企业知识库智能问答系统，支持上传企业内部文档，通过自然语言提问获取精准回答。

## 功能特性

- **多渠道文档导入** — 支持 PDF、Word、Markdown、TXT、Excel 单文件上传及文件夹批量导入
- **多种 Embedding 方案** — 支持本地模型（免费）、OpenAI、阿里云 DashScope 三种向量化方式
- **智能检索** — 基于 Chroma 向量数据库的语义检索，可调节 Top-K 检索数量
- **流式对话** — 基于 DeepSeek 大模型的上下文感知回答，带引用来源追溯
- **历史管理** — 问答记录自动保存，支持 CSV 导出

## 技术栈

| 组件 | 技术 |
|------|------|
| 前端框架 | Streamlit |
| 大语言模型 | DeepSeek (deepseek-chat / deepseek-coder) |
| 向量数据库 | ChromaDB |
| 文本分割 | LangChain Text Splitters |
| 文档解析 | PyPDF2, python-docx, openpyxl |
| 本地 Embedding | sentence-transformers (BAAI/bge-small-zh-v1.5) |
| 打包工具 | PyInstaller |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```env
DEEPSEEK_API_KEY=你的DeepSeek密钥
EMBEDDING_API_TYPE=local          # local / openai / dashscope
```

- 如果选择 `local`，首次运行时会自动下载 `BAAI/bge-small-zh-v1.5` 模型
- 如果选择 `openai` 或 `dashscope`，需额外配置对应的 `OPENAI_API_KEY` 或 `DASHSCOPE_API_KEY`

### 3. 启动应用

```bash
python run_app.py
```

浏览器访问 `http://localhost:8501` 即可使用。

## 项目结构

```
├── app.py              # Streamlit 主应用
├── run_app.py          # 启动脚本
├── config.py           # 配置管理
├── requirements.txt    # Python 依赖
├── core/               # 核心模块
│   ├── document_loader.py   # 文档加载
│   ├── embedding_client.py  # 向量化客户端
│   ├── llm_client.py        # DeepSeek LLM 客户端
│   ├── retriever.py         # 检索器
│   ├── text_splitter.py     # 文本分割
│   └── vector_store.py      # Chroma 向量存储
├── utils/              # 工具函数
│   ├── helpers.py
│   └── history_manager.py
├── data/               # 运行时数据（不提交到 Git）
│   ├── chroma_db/      # 向量数据库
│   └── documents/      # 上传的文档
└── tests/              # 测试
```

## 打包为 Windows 可执行文件

```bash
pyinstaller 知识库问答机器人.spec
```

打包产物在 `dist/` 目录下。

## 界面截图

> 将应用截图放入 `assets/` 目录，然后在下方引用。

![问答界面](assets/screenshot-qa.png)
![知识库管理](assets/screenshot-kb.png)
