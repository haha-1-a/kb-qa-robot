"""全面功能测试 — API + 核心模块 + 端到端"""
import json
import os
import sys
import tempfile
import time
import urllib.request

# UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API = "http://localhost:8000"
PASS = 0; FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1; print(f"  ✅ {name}")
    else:
        FAIL += 1; print(f"  ❌ {name}  {detail}")

def api_get(path):
    try:
        req = urllib.request.Request(f"{API}{path}")
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except Exception as e:
        return None, str(e)

def api_post(path, data=None, files=None):
    try:
        if files:
            import requests
            r = requests.post(f"{API}{path}", files=files, timeout=60)
            return r.status_code, r.json()
        else:
            body = json.dumps(data).encode() if data else None
            req = urllib.request.Request(f"{API}{path}", data=body,
                headers={"Content-Type": "application/json"} if body else {},
                method="POST")
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]
    except Exception as e:
        return None, str(e)

def api_delete(path):
    try:
        req = urllib.request.Request(f"{API}{path}", method="DELETE")
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]
    except Exception as e:
        return None, str(e)

# ═══════════════════════════════════════════════════════════
print("=" * 55)
print("  企业知识库问答机器人 — 全面功能测试")
print("=" * 55)

# ── 1. API 健康检查 & 基础端点 ─────────────────────────
print("\n📋 1. API 基础端点")

code, data = api_get("/health")
check("/health 可达", code == 200, str(code))
check("/health 返回 ok", isinstance(data, dict) and data.get("status") == "ok")

code, data = api_get("/stats")
check("/stats 可达", code == 200)
check("/stats 含必要字段", all(k in data for k in ["total_documents", "total_chunks", "db_size_mb"]))

code, data = api_get("/documents")
check("/documents 可达", code == 200)
check("/documents 返回列表", isinstance(data, list))

# ── 2. 文档上传 — 全部支持格式 ──────────────────────────
print("\n📋 2. 文档上传（7 种格式）")
import requests

test_files = []
test_dir = "tests/test_documents"
formats = {
    "财务报销流程.txt": "text/plain",
    "IT设备申领流程.md": "text/markdown",
    "员工培训制度.docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "差旅费用标准.pdf": "application/pdf",
    "2025年度培训计划.xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

for fname, mime in formats.items():
    fpath = os.path.join(test_dir, fname)
    if os.path.exists(fpath):
        try:
            r = requests.post(f"{API}/upload", files=[("files", (fname, open(fpath, "rb"), mime))], timeout=60)
            ok = fname in str(r.json().get("success", []))
            check(f"上传 {fname}", ok, str(r.json().get("failed", ""))[:80])
        except Exception as e:
            check(f"上传 {fname}", False, str(e)[:80])

# 生成并上传测试图片
from PIL import Image, ImageDraw
img = Image.new("RGB", (200, 100), color=(73, 109, 137))
draw = ImageDraw.Draw(img)
draw.text((10, 30), "Test Image 测试", fill=(255, 255, 255))
test_img = os.path.join(tempfile.gettempdir(), "test_img.png")
img.save(test_img)
try:
    r = requests.post(f"{API}/upload",
        files=[("files", ("test_img.png", open(test_img, "rb"), "image/png"))], timeout=60)
    check("上传 PNG 图片", "test_img.png" in str(r.json().get("success", [])))
except Exception as e:
    check("上传 PNG 图片", False, str(e)[:80])
os.remove(test_img)

# ── 3. 知识库统计验证 ──────────────────────────────────
print("\n📋 3. 知识库统计")

code, data = api_get("/stats")
check("文档数 > 0", data.get("total_documents", 0) > 0, f"docs={data.get('total_documents')}")
check("切片数 > 0", data.get("total_chunks", 0) > 0, f"chunks={data.get('total_chunks')}")
print(f"  📊 文档: {data.get('total_documents')}, 切片: {data.get('total_chunks')}, 大小: {data.get('db_size_mb')}MB")

code, data = api_get("/documents")
check("文档列表非空", len(data) > 0, f"got {len(data)} docs")

# ── 4. 语义检索 — 无 LLM 的纯检索 ──────────────────────
print("\n📋 4. 语义检索")

queries = [
    ("考勤制度", "考勤相关"),
    ("报销流程", "报销相关"),
    ("培训", "培训相关"),
]
for q, desc in queries:
    code, data = api_post("/search", {"query": q, "top_k": 3})
    has_results = code == 200 and len(data.get("results", [])) > 0
    check(f"检索 '{q}'", has_results,
          f"results={len(data.get('results', [])) if data else 0}")
    if has_results:
        top = data["results"][0]
        check(f"  -> 相关度 > 0.1", top["score"] > 0.1, f"score={top['score']:.3f}")

# 跨语言/模糊检索
code, data = api_post("/search", {"query": "请假", "top_k": 3})
has = code == 200 and len(data.get("results", [])) > 0
check("模糊检索 '请假'", has)

# ── 5. RAG 问答 — 完整链路 ──────────────────────────────
print("\n📋 5. RAG 问答（端到端）")

qa_tests = [
    ("公司的考勤制度是什么？", ["考勤", "时间", "迟到"]),
    ("报销流程有哪些步骤？", ["报销", "发票", "审核"]),
    ("IT设备怎么申请？", ["设备", "申请", "IT"]),
]
for q, keywords in qa_tests:
    code, data = api_post("/chat", {
        "question": q, "top_k": 4, "temperature": 0.3
    })
    ok = code == 200 and len(data.get("answer", "")) > 20
    check(f"问答: {q[:30]}...", ok,
          f"code={code}, len={len(data.get('answer','')) if data else 0}")

    if ok:
        answer = data["answer"]
        # 不应是"抱歉"（除非真的没内容）
        has_sources = len(data.get("sources", [])) > 0
        check(f"  -> 有引用来源", has_sources)
        # 答案不应太短
        check(f"  -> 回答充分 (>{'50'}字)", len(answer) > 50, f"len={len(answer)}")
        print(f"  💬 {answer[:100]}...")

# ── 6. 多轮对话上下文 ──────────────────────────────────
print("\n📋 6. 多轮对话")

code, data = api_post("/chat", {
    "question": "考勤制度",
    "top_k": 4,
    "history": [{"role": "user", "content": "我之前问过考勤的事"}]
})
check("带历史对话上下文", code == 200 and len(data.get("answer", "")) > 20)

# ── 7. 边界情况 ──────────────────────────────────────────
print("\n📋 7. 边界情况")

code, data = api_post("/search", {"query": "", "top_k": 3})
check("空查询（检索）", code == 200, str(code))  # 应不崩溃

code, data = api_post("/chat", {"question": "xyz123不存在的概念abc"})
ok = code == 200
check("不存在概念问答", ok, str(code))
if ok:
    check("  -> 返回答复不崩溃", len(data.get("answer", "")) > 0)

code, data = api_post("/search", {"query": "x" * 500, "top_k": 10})
check("超长查询", code == 200, str(code))

# ── 8. 文档管理 ──────────────────────────────────────────
print("\n📋 8. 文档管理")

code, data = api_get("/documents")
doc_count_before = len(data) if isinstance(data, list) else 0

# 删除一个文档
if doc_count_before > 0:
    src = data[0]["source"]
    encoded_src = urllib.parse.quote(src, safe='')
    code, data = api_delete(f"/documents/{encoded_src}")
    check(f"删除文档 '{src}'", code == 200, f"code={code}")

    code, data = api_get("/documents")
    doc_count_after = len(data) if isinstance(data, list) else 0
    check("文档数减少", doc_count_after == doc_count_before - 1,
          f"before={doc_count_before}, after={doc_count_after}")

# ── 9. Streamlit Web 界面可用性 ──────────────────────────
print("\n📋 9. Web 界面")

try:
    req = urllib.request.Request("http://localhost:8501")
    with urllib.request.urlopen(req, timeout=5) as r:
        html = r.read().decode()
        check("Streamlit 可访问（HTTP 200）", r.status == 200)
        # Streamlit 是 SPA，标题由 JS 渲染，不检查 HTML 源码
except Exception as e:
    check("Streamlit 可访问", False, str(e)[:80])

# ── 10. 配置导出 ────────────────────────────────────────
print("\n📋 10. 配置完整性")
from config import Config

checks_cfg = [
    ("DEEPSEEK_API_KEY", len(Config.DEEPSEEK_API_KEY) > 10),
    ("DEEPSEEK_BASE_URL", Config.DEEPSEEK_BASE_URL.startswith("https://")),
    ("CHUNK_SIZE", Config.CHUNK_SIZE == 500),
    ("CHUNK_OVERLAP", Config.CHUNK_OVERLAP == 50),
    ("CHROMA_PERSIST_PATH", "chroma_db" in Config.CHROMA_PERSIST_PATH),
    ("API_HOST 已配置", Config.API_HOST in ("0.0.0.0", "127.0.0.1", "localhost")),
    ("API_PORT 已配置", 1024 < Config.API_PORT < 65536),
    ("VISION_MODEL 已配置", len(Config.VISION_MODEL) > 0),
]
for name, cond in checks_cfg:
    check(name, cond)

# ═══════════════════════════════════════════════════════════
print(f"\n{'=' * 55}")
print(f"  通过: {PASS}  |  失败: {FAIL}  |  总计: {PASS + FAIL}")
if FAIL == 0:
    print("  🎉 全部功能正常！")
else:
    print(f"  ⚠️  {FAIL} 项异常，请检查")
print(f"{'=' * 55}")
