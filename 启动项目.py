import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"],
        cwd=ROOT / "backend",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    frontend = subprocess.Popen(
        ["node", "server.js"],
        cwd=ROOT / "frontend",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    time.sleep(2)
    webbrowser.open("http://localhost:8000")
    print("前后端已启动：前端 http://localhost:8000，后端 http://localhost:8001/docs")
    print("关闭此窗口将停止服务。")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for process in (frontend, backend):
            process.terminate()


if __name__ == "__main__":
    main()
