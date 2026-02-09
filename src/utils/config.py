from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Open WebUI / Ollama Settings
    OPENWEBUI_URL: str = "http://localhost:8080"
    OPENWEBUI_BASE_URL: Optional[str] = None # Support direct env override
    OPENWEBUI_TOKEN: Optional[str] = None    # Support static API keys (sk-)
    OPENWEBUI_EMAIL: str = ""
    OPENWEBUI_PASSWORD: str = ""
    OLLAMA_MODEL: str = "llama3.2:1b"
    
    POCKETBASE_URL: str = "https://pocketbase.thynaptic.com"
    POCKETBASE_ADMIN_EMAIL: str = ""
    POCKETBASE_ADMIN_PASSWORD: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
