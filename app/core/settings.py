from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///weather.db"
    DATA_DIR: Path = Path("wx_data")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()