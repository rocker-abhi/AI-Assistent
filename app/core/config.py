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

# Instantiate settings to be imported across the app
settings = Settings()
