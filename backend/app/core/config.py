import os
from functools import lru_cache
from pydantic import Field, field_validator, BaseModel

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    def SettingsConfigDict(**kwargs):
        return kwargs
    class BaseSettings(BaseModel):
        def __init__(self, **kwargs):
            env_defaults = {
                "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:"),
                "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                "JWT_SECRET": os.getenv("JWT_SECRET", "super-secret-key-1234567890-agenttrust-os"),
            }
            for k, v in env_defaults.items():
                if k in os.environ:
                    env_defaults[k] = os.environ[k]
                kwargs.setdefault(k.lower(), env_defaults[k])
            super().__init__(**kwargs)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "AgentTrust-OS"
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = Field(default=False, validation_alias="DEBUG")

    database_url: str = Field(default="sqlite+aiosqlite:///:memory:", validation_alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")

    jwt_secret: str = Field(default="secret-key-1234567890", validation_alias="JWT_SECRET")
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    jwt_refresh_token_expire_days: int = Field(
        default=30,
        validation_alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS",
    )

    frontend_url: str = Field(
        default="https://agnettrust-20.vercel.app",
        validation_alias="FRONTEND_URL",
    )
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,https://agnettrust-20.vercel.app,https://agenttrust-20.vercel.app",
        validation_alias="CORS_ORIGINS",
    )

    # Object Storage Configuration (Local vs S3/R2)
    storage_provider: str = Field(default="local", validation_alias="STORAGE_PROVIDER")
    s3_bucket_name: str = Field(default="", validation_alias="S3_BUCKET_NAME")
    s3_endpoint_url: str = Field(default="", validation_alias="S3_ENDPOINT_URL")
    s3_access_key_id: str = Field(default="", validation_alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: str = Field(default="", validation_alias="S3_SECRET_ACCESS_KEY")
    s3_region: str = Field(default="us-east-1", validation_alias="S3_REGION")

    # AI Perception Model Configuration
    yolo_model_path: str = Field(
        default="runs/detect/artifacts/training/doc_layout/real_yolo_002/train_run/weights/best.pt",
        validation_alias="YOLO_MODEL_PATH",
    )
    ocr_enabled: bool = Field(default=True, validation_alias="OCR_ENABLED")
    ocr_python_executable: str = Field(
        default="", validation_alias="OCR_PYTHON_EXECUTABLE"
    )
    ocr_timeout_seconds: int = Field(default=30, validation_alias="OCR_TIMEOUT_SECONDS")

    ai_api_key: str | None = Field(
        default=None,
        validation_alias="AI_API_KEY",
    )
    ai_provider: str | None = Field(
        default=None,
        validation_alias="AI_PROVIDER",
    )
    ai_model: str | None = Field(
        default=None,
        validation_alias="AI_MODEL",
    )

    default_language: str = Field(
        default="en",
        validation_alias="DEFAULT_LANGUAGE",
    )
    supported_languages: str = Field(
        default="en,hi",
        validation_alias="SUPPORTED_LANGUAGES",
    )

    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str, info) -> str:
        # In production, require real PostgreSQL database connection
        app_env = os.getenv("APP_ENV", "development").lower()
        if app_env == "production":
            if not value or value.startswith("sqlite"):
                raise ValueError(
                    "DATABASE_URL must be configured with a valid PostgreSQL connection in production. "
                    "In-memory/local SQLite is not permitted in production."
                )
        return value

    @field_validator("default_language")
    @classmethod
    def validate_default_language(cls, value: str) -> str:
        if value not in {"en", "hi"}:
            raise ValueError("DEFAULT_LANGUAGE must be 'en' or 'hi'")
        return value

    @field_validator("supported_languages")
    @classmethod
    def validate_supported_languages(cls, value: str) -> str:
        languages = {
            language.strip()
            for language in value.split(",")
            if language.strip()
        }

        if languages != {"en", "hi"}:
            raise ValueError(
                "SUPPORTED_LANGUAGES must contain exactly 'en' and 'hi'"
            )

        return "en,hi"


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()


settings = get_settings()