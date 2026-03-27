import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    app_name: str = "Nexus Agentic OS"
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    allow_mock_fallback: bool = os.getenv("ALLOW_MOCK_FALLBACK", "true").lower() == "true"


settings = Settings()
