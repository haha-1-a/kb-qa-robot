"""截取功能截图"""
import os, sys, io, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

def snap(page, name):
    path = os.path.join(OUT, name)
    page.screenshot(path=path)
    print(f"  -> {name} ({os.path.getsize(path)//1024}KB)")

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    vp = {"width": 1440, "height": 900}

    # ── 1. Streamlit 问答界面 ───────────────────────────
    print("1. 问答主界面...")
    ctx = browser.new_context(viewport=vp)
    page = ctx.new_page()
    page.goto("http://localhost:8501", timeout=30000, wait_until="networkidle")
    time.sleep(4)

    # 尝试在底部输入框输入问题
    try:
        # Streamlit chat_input
        chat = page.locator('[data-testid="stChatInputTextArea"]')
        if chat.count() > 0:
            chat.fill("IT设备怎么申请")
            time.sleep(0.5)
            chat.press("Enter")
            time.sleep(10)
            print("   Question submitted via stChatInput...")
        else:
            # fallback: 找任何可见的输入框
            inputs = page.locator("textarea, input[type='text']").all()
            for inp in inputs:
                if inp.is_visible():
                    inp.fill("IT设备怎么申请")
                    inp.press("Enter")
                    time.sleep(10)
                    print("   Question submitted via fallback...")
                    break
    except Exception as e:
        print(f"   Info: ({type(e).__name__})")

    snap(page, "screenshot-qa-full.png")
    ctx.close()

    # ── 2. 知识库管理 Tab ──────────────────────────────
    print("2. 知识库管理界面...")
    ctx2 = browser.new_context(viewport=vp)
    page2 = ctx2.new_page()
    page2.goto("http://localhost:8501", timeout=30000, wait_until="networkidle")
    time.sleep(3)
    try:
        tabs = page2.locator('button[role="tab"]').all()
        if len(tabs) >= 2:
            tabs[1].click()
            time.sleep(2)
            print("   Switched to KB tab")
    except Exception as e:
        print(f"   Info: ({type(e).__name__})")
    snap(page2, "screenshot-kb-full.png")
    ctx2.close()

    # ── 3. API Swagger 文档 ────────────────────────────
    print("3. API Swagger 文档...")
    ctx3 = browser.new_context(viewport=vp)
    page3 = ctx3.new_page()
    page3.goto("http://localhost:8000/docs", timeout=30000, wait_until="networkidle")
    time.sleep(3)
    snap(page3, "screenshot-api.png")
    ctx3.close()

    # ── 4. 侧边栏特写（窄视图露出侧边栏） ─────────────
    print("4. 侧边栏设置...")
    ctx4 = browser.new_context(viewport={"width": 1440, "height": 1000})
    page4 = ctx4.new_page()
    page4.goto("http://localhost:8501", timeout=30000, wait_until="networkidle")
    time.sleep(3)
    snap(page4, "screenshot-sidebar.png")
    ctx4.close()

    browser.close()
    print("\nAll done! Files in assets/:")
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".png"):
            print(f"  {f}")
