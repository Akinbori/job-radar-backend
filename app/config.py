from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "Bayo Job Radar API"
    recency_window_days: int = 3
    aggressive_mode: bool = True
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./job_radar.db")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    scan_limit_per_source: int = int(os.getenv("SCAN_LIMIT_PER_SOURCE", "25"))


settings = Settings()
