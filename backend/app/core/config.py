import json
import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings:
    def __init__(self) -> None:
        self.app_env = os.getenv("MARKETMIND_APP_ENV", "development")
        self.cors_origins = self._load_cors_origins()
        self.database_path = Path(os.getenv("MARKETMIND_DATABASE_PATH", BACKEND_DIR / "marketmind.db"))
        self.market_data_provider = os.getenv("MARKETMIND_MARKET_DATA_PROVIDER", "mock")
        self.alpha_vantage_api_key = os.getenv("MARKETMIND_ALPHA_VANTAGE_API_KEY", "")
        self.llm_provider = os.getenv("MARKETMIND_LLM_PROVIDER", "mock")
        self.llm_api_base_url = os.getenv("MARKETMIND_LLM_API_BASE_URL", "")
        self.llm_api_key = os.getenv("MARKETMIND_LLM_API_KEY", "")
        self.llm_model = os.getenv("MARKETMIND_LLM_MODEL", "")

    @staticmethod
    def _load_cors_origins() -> list[str]:
        raw_value = os.getenv("MARKETMIND_CORS_ORIGINS")
        if not raw_value:
            return ["http://localhost:5173", "http://127.0.0.1:5173"]

        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            return [origin.strip() for origin in raw_value.split(",") if origin.strip()]

        if isinstance(parsed, list) and all(isinstance(origin, str) for origin in parsed):
            return parsed

        return ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
