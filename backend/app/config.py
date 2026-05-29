from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "考研804知识库系统"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{Path(__file__).parent.parent.parent / 'data' / 'knowledge.db'}"
    UPLOAD_DIR: str = str(Path(__file__).parent.parent.parent / "data" / "uploads")
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://192.168.124.25:5173",
    ]
    ENABLE_CORS: bool = True  # set False in production .env

    # AI Provider Keys
    DEEPSEEK_API_KEY: str = ""

    # Default AI settings
    DEFAULT_AI_PROVIDER: str = "deepseek"

    # Few-shot training settings
    ENABLE_FEW_SHOT: bool = True
    MAX_FEW_SHOT_EXAMPLES: int = 3

    class Config:
        env_file = ".env"


settings = Settings()
