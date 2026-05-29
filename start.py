"""一键启动 考研804知识库系统 前后端服务"""

import subprocess
import sys
import time
import webbrowser
import signal
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "backend")
FRONTEND_DIR = os.path.join(ROOT, "frontend")

processes = []


def main():
    # 强制使用 UTF-8 避免 GBK 乱码
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 50)
    print("  考研804知识库系统 - 一键启动")
    print("=" * 50)
    print()

    # 启动后端
    print("[1/3] 启动后端服务 (FastAPI :8000)...")
    backend = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    processes.append(("后端", backend))

    # 启动前端
    print("[2/3] 启动前端服务 (Vite :5173)...")
    frontend = subprocess.Popen(
        ["cmd", "/c", "npm run dev"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    processes.append(("前端", frontend))

    # 等待后端就绪
    print("[3/3] 等待服务就绪...")
    backend_ready = False
    for _ in range(30):
        time.sleep(1)
        if backend.poll() is not None:
            break
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:8000/docs", timeout=1)
            backend_ready = True
            break
        except Exception:
            pass

    if not backend_ready:
        print("[警告] 后端可能尚未完全就绪，继续打开浏览器...")
    else:
        print("       后端就绪!")

    # 打开浏览器
    time.sleep(2)
    webbrowser.open("http://localhost:5173")
    print()
    print("=" * 50)
    print("  后端 : http://localhost:8000  (Swagger: /docs)")
    print("  前端 : http://localhost:5173")
    print("=" * 50)
    print()
    print("按 Ctrl+C 停止所有服务...")
    print()

    # 持续运行，监控子进程
    try:
        while True:
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"[错误] {name}服务意外退出 (code={proc.returncode})")
                    shutdown()
                    sys.exit(1)
                line = proc.stdout.readline()
                if line:
                    safe_print(f"  [{name}] {line.rstrip()}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        shutdown()


def safe_print(text):
    """安全打印，避免 GBK 编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))


def shutdown():
    for name, proc in processes:
        if proc.poll() is None:
            print(f"  停止{name}服务...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    print("已停止所有服务。")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    main()
