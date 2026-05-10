from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Knowledge Assistant"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_debug: bool = Field(default=True, alias="APP_DEBUG")

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    llm_model: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    llm_device: str = "cpu"
    llm_max_new_tokens: int = 256
    llm_temperature: float = 0.1

    qdrant_path: Path = Path("qdrant_data")
    qdrant_collection: str = "enterprise_knowledge"

    data_dir: Path = Path("data")
    upload_dir: Path = Path("data/uploads")
    pipeline_cache_dir: Path = Path("data/pipeline_cache")

    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 4
    max_context_characters: int = 5000
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    http_timeout_seconds: float = 10.0
    news_feed_urls: str = (
        "https://feeds.npr.org/1001/rss.xml,"
        "https://feeds.bbci.co.uk/news/world/rss.xml,"
        "https://feeds.bbci.co.uk/news/technology/rss.xml"
    )

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def allowed_origins_list(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]

    @property
    def news_feed_url_list(self) -> list[str]:
        return [item.strip() for item in self.news_feed_urls.split(",") if item.strip()]

    def ensure_directories(self) -> None:
        for path_value in [self.data_dir, self.upload_dir, self.pipeline_cache_dir, self.qdrant_path]:
            resolved = self.base_dir / path_value
            resolved.mkdir(parents=True, exist_ok=True)

    def resolve_path(self, path_value: Path) -> Path:
        return self.base_dir / path_value


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
