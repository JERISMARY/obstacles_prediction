from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "sih26_urban_intel"
    SECRET_KEY: str = "sih26-secret-key"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 500
    DEMO_MODE: bool = True
    YOLO_MODEL: str = "yolov8n.pt"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
