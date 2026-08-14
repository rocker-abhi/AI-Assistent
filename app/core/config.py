from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings and configurations.
    Values here are hardcoded defaults directly instead of using a .env file.
    """
    # General
    PROJECT_NAME: str = "Friday AI Assistant"
    VERSION: str = "1.0.0"
    
    # Server configuration (Hardcoded as requested)
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # CORS (For allowing the React/Vite frontend to connect)
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    # LLM Configuration
    LLM_MODEL: str = "deepseek-r1:1.5b"
    LLM_TEMPERATURE: float = 0.5
    MAX_HISTORY_MESSAGES: int = 10
    
    # TTS Configuration
    TTS_VOICE: str = "en-US-JennyNeural"
    TTS_RATE: str = "+17%"

    PRIMARY_DB: str = "postgresql+psycopg://abhishek:postgres@localhost:5432/assistant_db"

    GROK_API_KEY: str = "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"
    GROK_MODEL: str = "llama-3.1-8b-instant"

    WISPER_MODEL: str = "base"

# Instantiate settings to be imported across the app
settings = Settings()
