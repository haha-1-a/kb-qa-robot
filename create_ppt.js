const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "企业知识库问答机器人团队";
pres.title = "企业知识库问答机器人 — 项目介绍";

// ── 配色方案：深蓝 + 青色 ────────────────────────────
const C = {
  darkBg: "0D1B2A",   // 深色背景
  primary: "1B3A5C",  // 主色
  accent: "2EC4B6",   // 强调色
  white: "FFFFFF",
  lightGray: "E8ECEF",
  text: "2C3E50",
  muted: "7F8C8D",
};

// ── 截图路径 ─────────────────────────────────────────
const imgQA = path.resolve("assets/screenshot-qa-full.png");
const imgKB = path.resolve("assets/screenshot-kb-full.png");
const imgAPI = path.resolve("assets/screenshot-api.png");
const imgSidebar = path.resolve("assets/screenshot-sidebar.png");

const hasQA = fs.existsSync(imgQA);
const hasKB = fs.existsSync(imgKB);
const hasAPI = fs.existsSync(imgAPI);
const hasSidebar = fs.existsSync(imgSidebar);

// ═══════════════════════════════════════════════════════
// Slide 1: 封面
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.darkBg };

  slide.addText("企业知识库问答机器人", {
    x: 1, y: 1.2, w: 8, h: 1.2,
    fontSize: 40, fontFace: "Arial Black", color: C.white,
    bold: true, align: "center",
  });

  slide.addShape(pres.ShapeType.rect, {
    x: 3.5, y: 2.4, w: 3, h: 0.06,
    fill: { color: C.accent },
  });

  slide.addText("基于 RAG 架构的智能知识库问答系统", {
    x: 1, y: 2.7, w: 8, h: 0.8,
    fontSize: 18, fontFace: "Calibri", color: C.accent,
    align: "center",
  });

  slide.addText([
    { text: "课程：云计算与大数据应用开发\n", options: { fontSize: 14, color: C.muted, breakLine: true } },
    { text: "成员：XXX / XXX / XXX / XXX\n", options: { fontSize: 14, color: C.muted, breakLine: true } },
    { text: "2026 年 6 月", options: { fontSize: 14, color: C.muted } },
  ], { x: 1, y: 4.0, w: 8, h: 1.2, align: "center", fontFace: "Calibri" });
}

// ═══════════════════════════════════════════════════════
// Slide 2: 项目背景
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("项目背景", {
    x: 0.6, y: 0.4, w: 8, h: 0.8,
    fontSize: 32, fontFace: "Arial Black", color: C.primary, bold: true,
  });

  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 1.15, w: 1.8, h: 0.04, fill: { color: C.accent },
  });

  const items = [
    { icon: "🏢", title: "企业痛点", desc: "企业内部文档分散，员工查找制度流程耗时耗力，重复咨询 HR / IT / 行政效率低下" },
    { icon: "📚", title: "知识沉淀", desc: "大量制度文件、培训材料、报销流程等隐性知识未被有效组织和利用" },
    { icon: "🤖", title: "AI 赋能", desc: "借助大语言模型 + RAG 技术，将企业文档转化为可对话的知识库，即问即答" },
  ];

  items.forEach((item, i) => {
    const y = 1.6 + i * 1.2;
    slide.addShape(pres.ShapeType.roundRect, {
      x: 0.6, y: y, w: 8.8, h: 1.0,
      fill: { color: C.lightGray }, rectRadius: 0.1,
    });
    slide.addText(item.icon, { x: 0.8, y: y + 0.15, w: 0.6, h: 0.6, fontSize: 28 });
    slide.addText(item.title, {
      x: 1.5, y: y + 0.1, w: 7.5, h: 0.4,
      fontSize: 18, fontFace: "Arial Black", color: C.primary, bold: true,
    });
    slide.addText(item.desc, {
      x: 1.5, y: y + 0.5, w: 7.5, h: 0.4,
      fontSize: 13, fontFace: "Calibri", color: C.text,
    });
  });
}

// ═══════════════════════════════════════════════════════
// Slide 3: 项目目标
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("项目目标", {
    x: 0.6, y: 0.4, w: 8, h: 0.8,
    fontSize: 32, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 1.15, w: 1.8, h: 0.04, fill: { color: C.accent },
  });

  const goals = [
    { num: "01", title: "多格式知识库", desc: "支持 PDF / Word / Excel / 图片 / 视频等文档的结构化存储与语义检索" },
    { num: "02", title: "智能问答", desc: "基于 DeepSeek 大模型 + RAG 架构，理解用户意图，精准回答并附引用来源" },
    { num: "03", title: "多端访问", desc: "Web 界面（Streamlit）+ RESTful API（FastAPI）+ Docker 容器化一键部署" },
    { num: "04", title: "多模态扩展", desc: "图片通过视觉模型理解，视频通过 Whisper 语音识别，纳入知识库" },
  ];

  goals.forEach((g, i) => {
    const x = 0.6 + (i % 2) * 4.5;
    const y = 1.5 + Math.floor(i / 2) * 2.0;

    slide.addText(g.num, {
      x: x, y: y, w: 1.2, h: 1.2,
      fontSize: 36, fontFace: "Arial Black", color: C.accent, bold: true,
    });
    slide.addText(g.title, {
      x: x + 1.3, y: y + 0.1, w: 3.0, h: 0.4,
      fontSize: 18, fontFace: "Arial Black", color: C.primary, bold: true,
    });
    slide.addText(g.desc, {
      x: x + 1.3, y: y + 0.55, w: 3.0, h: 0.5,
      fontSize: 12, fontFace: "Calibri", color: C.text,
    });
  });
}

// ═══════════════════════════════════════════════════════
// Slide 4: 技术架构
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("技术架构", {
    x: 0.6, y: 0.4, w: 8, h: 0.8,
    fontSize: 32, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 1.15, w: 1.8, h: 0.04, fill: { color: C.accent },
  });

  // RAG 流程图
  const flowSteps = [
    { label: "文档上传", sub: "PDF/Word/Excel\n图片/视频", color: C.primary },
    { label: "文本提取", sub: "多模态处理\nVL + Whisper", color: "2C5F7C" },
    { label: "向量嵌入", sub: "BGE / OpenAI\nDashScope", color: "1A7293" },
    { label: "ChromaDB", sub: "语义检索\nCosine 相似度", color: "0D8FA0" },
    { label: "LLM 生成", sub: "DeepSeek\n带来源引用", color: C.accent },
  ];

  flowSteps.forEach((step, i) => {
    const x = 0.7 + i * 1.85;
    slide.addShape(pres.ShapeType.roundRect, {
      x: x, y: 1.6, w: 1.6, h: 1.4,
      fill: { color: step.color }, rectRadius: 0.1,
    });
    slide.addText(step.label, {
      x: x, y: 1.7, w: 1.6, h: 0.5,
      fontSize: 14, fontFace: "Arial Black", color: C.white, bold: true, align: "center",
    });
    slide.addText(step.sub, {
      x: x, y: 2.15, w: 1.6, h: 0.7,
      fontSize: 10, fontFace: "Calibri", color: C.white, align: "center",
    });

    // 箭头
    if (i < flowSteps.length - 1) {
      slide.addText("→", {
        x: x + 1.55, y: 2.0, w: 0.35, h: 0.5,
        fontSize: 22, color: C.muted, align: "center",
      });
    }
  });

  // 技术栈表格
  const techs = [
    ["层级", "技术选型"],
    ["LLM 大模型", "DeepSeek (deepseek-chat)"],
    ["向量数据库", "ChromaDB"],
    ["Embedding", "BGE / OpenAI / DashScope"],
    ["前端框架", "Streamlit"],
    ["API 服务", "FastAPI (RESTful)"],
    ["语音识别", "OpenAI Whisper"],
    ["容器部署", "Docker + Compose"],
  ];

  const tableY = 3.4;
  techs.forEach((row, i) => {
    const isHeader = i === 0;
    const rowY = tableY + i * 0.32;
    slide.addShape(pres.ShapeType.rect, {
      x: 0.8, y: rowY, w: 1.8, h: 0.3,
      fill: { color: isHeader ? C.primary : C.lightGray },
    });
    slide.addText(row[0], {
      x: 0.8, y: rowY, w: 1.8, h: 0.3,
      fontSize: 11, fontFace: "Calibri",
      color: isHeader ? C.white : C.text,
      bold: isHeader, align: "center",
    });
    slide.addShape(pres.ShapeType.rect, {
      x: 2.6, y: rowY, w: 6.6, h: 0.3,
      fill: { color: isHeader ? C.primary : C.white },
    });
    slide.addText(row[1], {
      x: 2.6, y: rowY, w: 6.6, h: 0.3,
      fontSize: 11, fontFace: "Calibri",
      color: isHeader ? C.white : C.text,
      align: "center",
    });
  });
}

// ═══════════════════════════════════════════════════════
// Slide 5: 问答功能展示
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("功能展示 — 智能问答", {
    x: 0.6, y: 0.25, w: 8, h: 0.6,
    fontSize: 26, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 0.8, w: 1.6, h: 0.04, fill: { color: C.accent },
  });

  slide.addText([
    { text: "• 输入自然语言问题「IT设备怎么申请」", options: {} },
  ], { x: 0.7, y: 1.0, w: 8.5, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.text });
  slide.addText([
    { text: "• AI 检索知识库 → 精准回答 + 引用来源追溯", options: {} },
  ], { x: 0.7, y: 1.25, w: 8.5, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.text });

  if (hasQA) {
    slide.addImage({ path: imgQA, x: 0.6, y: 1.6, w: 8.8, h: 3.8 });
  } else {
    slide.addText("[ 问答界面截图 ]", {
      x: 1, y: 2.5, w: 8, h: 2, fontSize: 16, color: C.muted, align: "center",
    });
  }
}

// ═══════════════════════════════════════════════════════
// Slide 6: 知识库管理展示
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("功能展示 — 知识库管理", {
    x: 0.6, y: 0.25, w: 8, h: 0.6,
    fontSize: 26, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 0.8, w: 1.6, h: 0.04, fill: { color: C.accent },
  });

  slide.addText([
    { text: "• 支持 8 种格式：PDF/DOCX/MD/TXT/XLSX/JPG/PNG/MP4   |   批量导入 + 文件夹导入\n", options: { breakLine: true } },
    { text: "• 实时统计：文档数/切片数/数据库大小   |   单个删除 + 清空管理", options: {} },
  ], { x: 0.7, y: 1.0, w: 8.8, h: 0.6, fontSize: 12, fontFace: "Calibri", color: C.text });

  if (hasKB) {
    slide.addImage({ path: imgKB, x: 0.6, y: 1.6, w: 8.8, h: 3.8 });
  } else {
    slide.addText("[ 知识库管理截图 ]", {
      x: 1, y: 2.5, w: 8, h: 2, fontSize: 16, color: C.muted, align: "center",
    });
  }
}

// ═══════════════════════════════════════════════════════
// Slide 7: 侧边栏 + 设置功能
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("功能展示 — 配置与历史", {
    x: 0.6, y: 0.25, w: 8, h: 0.6,
    fontSize: 26, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 0.8, w: 1.6, h: 0.04, fill: { color: C.accent },
  });

  // 左侧功能点
  const features = [
    { icon: "🔧", title: "Embedding 切换", desc: "本地 BGE / OpenAI / DashScope 三种向量化方案自由选择" },
    { icon: "🎚️", title: "检索调参", desc: "Top-K 检索数量、温度参数、LLM 模型实时调节" },
    { icon: "📜", title: "历史管理", desc: "问答记录自动保存、CSV 导出、按时间回溯" },
    { icon: "🔄", title: "缓存控制", desc: "一键清除缓存，强制刷新 ChromaDB 连接" },
  ];

  features.forEach((f, i) => {
    const y = 1.15 + i * 1.05;
    slide.addShape(pres.ShapeType.roundRect, {
      x: 0.6, y: y, w: 4.6, h: 0.9,
      fill: { color: i % 2 === 0 ? C.lightGray : C.white },
      rectRadius: 0.08,
    });
    slide.addText(f.icon, { x: 0.8, y: y + 0.15, w: 0.5, h: 0.5, fontSize: 24 });
    slide.addText(f.title, {
      x: 1.4, y: y + 0.05, w: 3.5, h: 0.35,
      fontSize: 15, fontFace: "Arial Black", color: C.primary, bold: true,
    });
    slide.addText(f.desc, {
      x: 1.4, y: y + 0.4, w: 3.5, h: 0.4,
      fontSize: 11, fontFace: "Calibri", color: C.text,
    });
  });

  // 右侧截图
  if (hasSidebar) {
    slide.addImage({ path: imgSidebar, x: 5.4, y: 1.1, w: 4.3, h: 4.3 });
  }
}

// ═══════════════════════════════════════════════════════
// Slide 8: API 与部署
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("API 服务与部署", {
    x: 0.6, y: 0.4, w: 8, h: 0.8,
    fontSize: 32, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 1.15, w: 1.8, h: 0.04, fill: { color: C.accent },
  });

  // API 端点表
  const apiRows = [
    ["端点", "方法", "功能"],
    ["/chat", "POST", "RAG 智能问答"],
    ["/search", "POST", "语义检索"],
    ["/upload", "POST", "文档上传"],
    ["/stats", "GET", "知识库统计"],
    ["/documents", "GET/DELETE", "文档管理"],
  ];

  apiRows.forEach((row, i) => {
    const isH = i === 0;
    const y = 1.5 + i * 0.38;
    [row[0], row[1], row[2]].forEach((cell, j) => {
      const cx = 0.7 + j * [3.0, 1.5, 4.0].slice(0, j).reduce((a, b) => a + b, 0);
      const cw = [3.0, 1.5, 4.0][j];
      slide.addShape(pres.ShapeType.rect, {
        x: cx, y: y, w: cw, h: 0.35,
        fill: { color: isH ? C.primary : (i % 2 === 0 ? C.lightGray : C.white) },
      });
      slide.addText(cell, {
        x: cx, y: y, w: cw, h: 0.35,
        fontSize: 12, fontFace: "Consolas",
        color: isH ? C.white : C.text,
        bold: isH, align: "center",
      });
    });
  });

  // Docker
  slide.addText("Docker 部署", {
    x: 0.7, y: 4.0, w: 4, h: 0.4,
    fontSize: 18, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addText("docker compose up\n→ Streamlit :8501  +  API :8000", {
    x: 0.7, y: 4.35, w: 4, h: 0.8,
    fontSize: 12, fontFace: "Consolas", color: C.text,
  });

  // 技术亮点
  slide.addShape(pres.ShapeType.roundRect, {
    x: 5.5, y: 3.8, w: 3.8, h: 1.4,
    fill: { color: C.lightGray }, rectRadius: 0.1,
  });
  slide.addText([
    { text: "技术亮点\n", options: { bold: true, fontSize: 14, color: C.primary, breakLine: true } },
    { text: "• 云计算平台可部署\n• Docker 容器化\n• RESTful API 标准化\n• 移动端可访问", options: { fontSize: 11, color: C.text } },
  ], { x: 5.7, y: 3.85, w: 3.4, h: 1.3, fontFace: "Calibri" });
}

// ═══════════════════════════════════════════════════════
// Slide 9: RAG 实现方法
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("核心实现 — RAG 检索增强生成", {
    x: 0.6, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 0.95, w: 2.2, h: 0.04, fill: { color: C.accent },
  });

  // 左侧流程步骤
  const steps = [
    { phase: "文档预处理", items: "LangChain RecursiveCharacterTextSplitter\nchunk_size=500, overlap=50\n中文优化分隔符" },
    { phase: "向量化", items: "BAAI/bge-small-zh-v1.5 本地模型\n512 维向量, cosine 相似度\n支持 OpenAI / DashScope 切换" },
    { phase: "语义检索", items: "ChromaDB 持久化存储\nTop-K 可调 (1-10)\n余弦距离 → 相似度分数" },
    { phase: "生成回答", items: "DeepSeek API (OpenAI 兼容)\n上下文拼接 + 系统提示词\n引用来源追溯 + 多轮对话" },
  ];

  steps.forEach((s, i) => {
    const y = 1.2 + i * 1.05;
    slide.addShape(pres.ShapeType.roundRect, {
      x: 0.7, y: y, w: 4.5, h: 0.95,
      fill: { color: i % 2 === 0 ? C.lightGray : C.white },
      rectRadius: 0.08,
    });
    slide.addText(s.phase, {
      x: 0.9, y: y + 0.05, w: 4, h: 0.35,
      fontSize: 16, fontFace: "Arial Black", color: C.primary, bold: true,
    });
    slide.addText(s.items, {
      x: 0.9, y: y + 0.35, w: 4, h: 0.6,
      fontSize: 11, fontFace: "Calibri", color: C.text,
    });
  });

  // 右侧代码示例
  slide.addShape(pres.ShapeType.roundRect, {
    x: 5.5, y: 1.2, w: 4.0, h: 4.2,
    fill: { color: C.darkBg }, rectRadius: 0.1,
  });
  slide.addText("核心代码（Python）", {
    x: 5.7, y: 1.3, w: 3.6, h: 0.35,
    fontSize: 12, fontFace: "Arial Black", color: C.accent,
  });
  slide.addText(
`// 检索
contexts = retriever.retrieve(
  user_input, top_k=4
)
// → [(text, meta, score), ...]

// 构建 Prompt
prompt = f\"\"\"
参考资料：
{context_text}

问题：{query}
\"\"\"

// LLM 生成
answer = llm.chat([
  {role:"system", content:SYSTEM_PROMPT},
  {role:"user", content:prompt}
])`, {
    x: 5.7, y: 1.7, w: 3.6, h: 3.5,
    fontSize: 9, fontFace: "Consolas", color: C.lightGray,
  });
}

// ═══════════════════════════════════════════════════════
// Slide 10: 多模态处理详解
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("多模态 RAG 处理流程", {
    x: 0.6, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 0.95, w: 2.2, h: 0.04, fill: { color: C.accent },
  });

  // 图片处理流程
  slide.addText("图片 RAG", {
    x: 0.7, y: 1.2, w: 4, h: 0.4,
    fontSize: 18, fontFace: "Arial Black", color: C.primary, bold: true,
  });

  const imgSteps = ["图片上传\nJPG/PNG", "PIL 压缩\n≤1024px", "Base64\n编码", "DeepSeek VL\n视觉理解", "文本描述\n→ 向量库"];
  imgSteps.forEach((t, i) => {
    const x = 0.6 + i * 1.8;
    slide.addShape(pres.ShapeType.roundRect, {
      x: x, y: 1.7, w: 1.55, h: 1.0,
      fill: { color: C.primary }, rectRadius: 0.08,
    });
    slide.addText(t, {
      x: x, y: 1.75, w: 1.55, h: 0.9,
      fontSize: 10, fontFace: "Calibri", color: C.white, align: "center",
    });
    if (i < imgSteps.length - 1) {
      slide.addText("→", { x: x + 1.5, y: 2.0, w: 0.35, h: 0.4, fontSize: 18, color: C.accent });
    }
  });

  // 视频处理流程
  slide.addText("视频 RAG", {
    x: 0.7, y: 3.0, w: 4, h: 0.4,
    fontSize: 18, fontFace: "Arial Black", color: C.primary, bold: true,
  });

  const vidSteps = ["视频上传\nMP4", "MoviePy\n提取音频", "Whisper\n语音识别", "中文转录\n文本", "文本→ 向量库"];
  vidSteps.forEach((t, i) => {
    const x = 0.6 + i * 1.8;
    slide.addShape(pres.ShapeType.roundRect, {
      x: x, y: 3.5, w: 1.55, h: 1.0,
      fill: { color: "2C5F7C" }, rectRadius: 0.08,
    });
    slide.addText(t, {
      x: x, y: 3.55, w: 1.55, h: 0.9,
      fontSize: 10, fontFace: "Calibri", color: C.white, align: "center",
    });
    if (i < vidSteps.length - 1) {
      slide.addText("→", { x: x + 1.5, y: 3.8, w: 0.35, h: 0.4, fontSize: 18, color: C.accent });
    }
  });

  // Fallback 说明
  slide.addShape(pres.ShapeType.roundRect, {
    x: 0.7, y: 4.7, w: 8.5, h: 0.6,
    fill: { color: C.lightGray }, rectRadius: 0.08,
  });
  slide.addText("💡 VL 模型不可用时，自动降级为图片元数据描述（尺寸、格式），确保图片仍可被检索", {
    x: 0.9, y: 4.75, w: 8, h: 0.45,
    fontSize: 12, fontFace: "Calibri", color: C.text,
  });
}

// ═══════════════════════════════════════════════════════
// Slide 11: Docker 容器化部署
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("容器化部署 — Docker", {
    x: 0.6, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 0.95, w: 2.2, h: 0.04, fill: { color: C.accent },
  });

  // docker-compose 代码
  slide.addText("docker-compose.yml", {
    x: 0.7, y: 1.15, w: 4.5, h: 0.35,
    fontSize: 14, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.roundRect, {
    x: 0.7, y: 1.55, w: 4.6, h: 3.2,
    fill: { color: C.darkBg }, rectRadius: 0.1,
  });
  slide.addText(
`services:
  streamlit:
    build: .
    ports: ["8501:8501"]
    command: python run_app.py
    volumes: [./data:/app/data]
    restart: unless-stopped

  api:
    build: .
    ports: ["8000:8000"]
    command: uvicorn api:app \\
      --host 0.0.0.0 --port 8000
    restart: unless-stopped`, {
    x: 0.9, y: 1.65, w: 4.2, h: 2.9,
    fontSize: 9, fontFace: "Consolas", color: C.lightGray,
  });

  // 架构说明
  slide.addText("部署架构", {
    x: 5.8, y: 1.15, w: 3.5, h: 0.35,
    fontSize: 14, fontFace: "Arial Black", color: C.primary, bold: true,
  });

  const archItems = [
    { title: "多阶段构建", desc: "Python 3.11-slim 基础镜像\npip 安装依赖 → 复制源码" },
    { title: "数据持久化", desc: "ChromaDB 向量库 + 文档\n通过 volume 挂载宿主机" },
    { title: "环境变量注入", desc: "API Key 通过 .env 传入\n生产环境安全隔离" },
    { title: "自愈重启", desc: "restart: unless-stopped\n进程崩溃自动恢复" },
  ];

  archItems.forEach((item, i) => {
    const y = 1.6 + i * 0.95;
    slide.addShape(pres.ShapeType.roundRect, {
      x: 5.8, y: y, w: 3.7, h: 0.8,
      fill: { color: i % 2 === 0 ? C.lightGray : C.white },
      rectRadius: 0.08,
    });
    slide.addText(item.title, {
      x: 6.0, y: y + 0.05, w: 3.3, h: 0.3,
      fontSize: 13, fontFace: "Arial Black", color: C.primary, bold: true,
    });
    slide.addText(item.desc, {
      x: 6.0, y: y + 0.35, w: 3.3, h: 0.4,
      fontSize: 10, fontFace: "Calibri", color: C.text,
    });
  });

  // 一行快捷命令
  slide.addShape(pres.ShapeType.roundRect, {
    x: 0.7, y: 5.0, w: 8.5, h: 0.5,
    fill: { color: C.primary }, rectRadius: 0.08,
  });
  slide.addText("$ docker compose up  →  Streamlit http://localhost:8501  +  API http://localhost:8000/docs", {
    x: 1, y: 5.05, w: 8, h: 0.4,
    fontSize: 13, fontFace: "Consolas", color: C.white, align: "center",
  });
}

// ═══════════════════════════════════════════════════════
// Slide 12: 项目难点与解决方案
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  slide.addText("技术难点与解决方案", {
    x: 0.6, y: 0.3, w: 8, h: 0.7,
    fontSize: 28, fontFace: "Arial Black", color: C.primary, bold: true,
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 0.6, y: 0.95, w: 2.2, h: 0.04, fill: { color: C.accent },
  });

  const challenges = [
    {
      problem: "ChromaDB metadata 为 None 导致崩溃",
      solution: "检索器中增加 None 检查：meta = metas[i] if metas[i] is not None else {}",
      tech: "容错处理",
    },
    {
      problem: "Streamlit 缓存导致知识库数据不更新",
      solution: "移除 VectorStore 的 @st.cache_resource 装饰器，每次查询实时读取 ChromaDB",
      tech: "状态管理",
    },
    {
      problem: "中文长文本的语义分割精度问题",
      solution: "使用 RecursiveCharacterTextSplitter，中文句号/换行作为分隔符，chunk_size=500",
      tech: "文本处理",
    },
    {
      problem: "多进程同时访问 SQLite 锁冲突",
      solution: "API 与 Streamlit 共享同一 ChromaDB 路径，读操作并发，写操作由 API 统一处理",
      tech: "并发控制",
    },
    {
      problem: "VL 模型不可用时的图片处理",
      solution: "设计降级策略：VL 失败 → 提取图片尺寸/格式等元数据作为文本描述，确保可检索",
      tech: "降级设计",
    },
  ];

  challenges.forEach((c, i) => {
    const y = 1.2 + i * 0.85;
    // 问题
    slide.addShape(pres.ShapeType.roundRect, {
      x: 0.7, y: y, w: 4.2, h: 0.7,
      fill: { color: "FDEBD0" }, rectRadius: 0.08,
    });
    slide.addText(`❌ ${c.problem}`, {
      x: 0.9, y: y + 0.1, w: 3.8, h: 0.5,
      fontSize: 11, fontFace: "Calibri", color: C.text,
    });

    // 解决
    slide.addShape(pres.ShapeType.roundRect, {
      x: 5.1, y: y, w: 4.2, h: 0.7,
      fill: { color: "D5F5E3" }, rectRadius: 0.08,
    });
    slide.addText(`✅ ${c.solution}`, {
      x: 5.3, y: y + 0.1, w: 3.8, h: 0.5,
      fontSize: 11, fontFace: "Calibri", color: C.text,
    });

    // 标签
    slide.addShape(pres.ShapeType.roundRect, {
      x: 4.85, y: y + 0.2, w: 0.5, h: 0.3,
      fill: { color: C.accent }, rectRadius: 0.05,
    });
    slide.addText(c.tech, {
      x: 4.85, y: y + 0.2, w: 0.5, h: 0.3,
      fontSize: 7, fontFace: "Calibri", color: C.white, align: "center",
    });
  });
}

// ═══════════════════════════════════════════════════════
// Slide 13: 总结
// ═══════════════════════════════════════════════════════
{
  const slide = pres.addSlide();
  slide.background = { color: C.darkBg };

  slide.addText("总结与展望", {
    x: 1, y: 0.4, w: 8, h: 0.7,
    fontSize: 32, fontFace: "Arial Black", color: C.white, bold: true, align: "center",
  });
  slide.addShape(pres.ShapeType.rect, {
    x: 3.5, y: 1.05, w: 3, h: 0.04, fill: { color: C.accent },
  });

  const highlights = [
    "✅ 完整 RAG 链路 — 文档加载 → 文本分割 → 向量嵌入 → 语义检索 → LLM 生成",
    "✅ 多模态支持 — 文本 + 图片（VL） + 视频（Whisper）全格式覆盖",
    "✅ 多端访问 — Streamlit Web 界面 + FastAPI RESTful + Docker 一键部署",
    "✅ 灵活 Embedding — 本地免费 BGE / OpenAI / 阿里云 DashScope 三种切换",
    "✅ 来源追溯 — 每条回答标注引用文档和相关度分数",
    "✅ 工程化实践 — .env 配置 / 容错处理 / 降级策略 / 容器化部署",
  ];

  highlights.forEach((h, i) => {
    slide.addText(h, {
      x: 1.5, y: 1.3 + i * 0.5, w: 7.5, h: 0.45,
      fontSize: 14, fontFace: "Calibri", color: C.white,
    });
  });

  // 成员分工
  slide.addShape(pres.ShapeType.rect, {
    x: 2.5, y: 4.3, w: 5, h: 0.04, fill: { color: C.accent },
  });
  slide.addText("团队成员分工", {
    x: 1, y: 4.4, w: 8, h: 0.35,
    fontSize: 16, fontFace: "Arial Black", color: C.accent, align: "center",
  });
  slide.addText([
    { text: "XXX（组长）: 项目架构 + RAG 核心    ", options: {} },
    { text: "XXX: 多模态 + API 开发    ", options: {} },
    { text: "XXX: 前端 + Docker 部署    ", options: {} },
    { text: "XXX: 测试 + 文档", options: {} },
  ], { x: 0.5, y: 4.85, w: 9, h: 0.5, fontSize: 11, fontFace: "Calibri", color: C.lightGray, align: "center" });
}

// ═══════════════════════════════════════════════════════
pres.writeFile({ fileName: "项目介绍_企业知识库问答机器人.pptx" })
  .then(() => console.log("PPT 已生成: 项目介绍_企业知识库问答机器人.pptx"))
  .catch(err => console.error("生成失败:", err));
