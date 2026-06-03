"""启动 FastAPI 服务"""
import os
import sys

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

if __name__ == "__main__":
    import uvicorn
    from config import Config
    uvicorn.run("api:app", host=Config.API_HOST, port=Config.API_PORT, reload=True)
