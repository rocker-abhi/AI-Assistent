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
    LLM_MODEL: str = "llama3.2:1b"
    LLM_TEMPERATURE: float = 0.5
    
    # TTS Configuration
    TTS_VOICE: str = "en-US-JennyNeural"
    TTS_RATE: str = "+17%"

    PRIMARY_DB: str = "postgresql+psycopg://abhishek:postgres@localhost:5432/assistant_db"

# Instantiate settings to be imported across the app
settings = Settings()
