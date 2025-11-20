from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "EventAI"
    app_version: str = "1.0.0"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg2://postgres:admin@localhost:5432/eventai_db"
    async_database_url: str = "postgresql+asyncpg://postgres:admin@localhost:5432/eventai_db"

    secret_key: str = "supersecret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    redis_url: str = "redis://localhost:6379/0"

    mail_username: str = "your-email@gmail.com"
    mail_password: str = "your-app-password"
    mail_from: str = "noreply@eventai.com"
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587

    huggingface_token: str = "your-huggingface-token"

    class Config:
        env_file = ".env"
        extra = "ignore"  # optional if you prefer strict but we’ll relax it below

settings = Settings()
