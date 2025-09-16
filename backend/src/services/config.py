import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_request_delay: float = 0.0
    
    # Data Configuration
    data_dir: str = "./data"
    logs_dir: str = "./logs"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Crawler Configuration
    run_sources: str = "openai.com,anthropic.com,microsoft.com,google.com,meta.com"
    cron_time: str = "08:30"
    min_score_default: int = 60
    timezone: str = "Europe/London"
    crawler_days_back: int = 7
    max_stories_per_source: int = 20
    
    @property
    def source_list(self) -> List[str]:
        return [s.strip() for s in self.run_sources.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
