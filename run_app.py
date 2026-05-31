"""知识库问答机器人启动器"""
import os
import sys

# 禁用 Streamlit 交互提示
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "false"
os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"

# 确保工作目录在 exe 所在目录
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

# 创建 Streamlit 配置，跳过邮箱提示和开发模式警告
streamlit_dir = os.path.join(os.path.expanduser("~"), ".streamlit")
os.makedirs(streamlit_dir, exist_ok=True)

creds_path = os.path.join(streamlit_dir, "credentials.toml")
if not os.path.exists(creds_path):
    with open(creds_path, "w") as f:
        f.write('[general]\nemail = "kb-user@company.com"\n')

config_path = os.path.join(streamlit_dir, "config.toml")
with open(config_path, "w") as f:
    f.write("""[browser]
gatherUsageStats = false

[server]
headless = false

[global]
developmentMode = false
""")

from streamlit.web import cli as stcli

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    args = ["streamlit", "run", app_path]
    args.extend(sys.argv[1:])
    sys.argv = args
    sys.exit(stcli.main())
