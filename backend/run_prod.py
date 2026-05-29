"""Production server entry point.

Usage:
    python run_prod.py                   # default port 8000
    PORT=8080 python run_prod.py         # custom port (Render sets $PORT)
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
    )
