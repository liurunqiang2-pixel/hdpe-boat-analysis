from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "HDPE Ship Design Workbench"
    database_url: str = "sqlite:///./data/hdpe_design.db"
    allow_origins: str = "*"


settings = Settings()
