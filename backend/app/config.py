from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    APP_NAME: str = "考研804知识库系统"
    APP_MODE: str = "single_user"
    APP_USER_LABEL: str = "默认学习者"

    # Default: relative to project root. Set DATA_DIR env var on Render.
    DATA_DIR: str = str(Path(__file__).parent.parent.parent / "data")
    DATABASE_URL: str = ""
    UPLOAD_DIR: str = ""

    def model_post_init(self, _context):
        db_path = Path(self.DATA_DIR) / "knowledge.db"
        self.DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
        uploads = Path(self.DATA_DIR) / "uploads"
        self.UPLOAD_DIR = str(uploads)
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://192.168.124.25:5173",
    ]
    ENABLE_CORS: bool = True  # set False in production .env

    # AI Provider Keys
    DEEPSEEK_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Default AI settings
    DEFAULT_AI_PROVIDER: str = "deepseek"

    # Few-shot training settings
    ENABLE_FEW_SHOT: bool = True
    MAX_FEW_SHOT_EXAMPLES: int = 3

    # JWT Auth
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # Initial admin account
    INIT_ADMIN_USERNAME: str = "admin"
    INIT_ADMIN_PASSWORD: str = "admin123"


settings = Settings()
