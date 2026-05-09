from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Groq
    groq_api_key: str = ""
    groq_vision_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    groq_text_model: str = "llama-3.1-8b-instant"

    # HuggingFace fallback
    hf_token: str = ""
    hf_vision_model: str = "Qwen/Qwen2-VL-7B-Instruct"

    # Langfuse
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # App
    log_level: str = "INFO"
    app_env: str = "development"
    max_image_size_mb: int = 4


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
