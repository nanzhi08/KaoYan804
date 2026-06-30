import uvicorn
import subprocess
import sys


def _check_port(port: int) -> None:
    """Warn if the port is already in use (stale process from previous run)."""
    try:
        out = subprocess.check_output(
            ["netstat", "-ano"], text=True, errors="replace"
        )
        for line in out.splitlines():
            if f":{port} " in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                print(f"[WARN] Port {port} is already in use by PID {pid}.")
                print(f"       Run: taskkill /F /PID {pid}")
                print(f"       Or use: python start.py from project root")
                return
    except Exception:
        pass


if __name__ == "__main__":
    _check_port(8000)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
