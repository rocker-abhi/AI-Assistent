from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices

class Settings(BaseSettings):
    """
    Application settings and configurations loaded strictly from environment variables and .env file.
    All default values have been removed; all settings are strictly sourced from the environment.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General Project Info
    PROJECT_NAME: str
    VERSION: str

    # Server Configuration
    HOST: str
    PORT: int
    CORS_ORIGINS: List[str]

    # Database Configuration
    PRIMARY_DB: str

    # LLM Provider: "groq" or "ollama"
    LLM_PROVIDER: str

    # Groq LLM Configuration
    GROQ_API_KEY: str = Field(validation_alias=AliasChoices("GROQ_API_KEY", "GROK_API_KEY"))
    GROQ_MODEL: str = Field(validation_alias=AliasChoices("GROQ_MODEL", "GROK_MODEL"))
    GROQ_TEMPERATURE: float

    # Ollama LLM Configuration
    OLLAMA_BASE_URL: str
    OLLAMA_MODEL: str = Field(validation_alias=AliasChoices("OLLAMA_MODEL", "LLM_MODEL"))
    OLLAMA_TEMPERATURE: float = Field(validation_alias=AliasChoices("OLLAMA_TEMPERATURE", "LLM_TEMPERATURE"))

    # Conversation History
    MAX_HISTORY_MESSAGES: int

    # TTS Configuration (Edge TTS)
    TTS_VOICE: str
    TTS_RATE: str

    # Speech-to-Text Configuration (Whisper)
    WISPER_MODEL: str

    # Backward compatibility properties
    @property
    def LLM_MODEL(self) -> str:
        return self.OLLAMA_MODEL

    @property
    def LLM_TEMPERATURE(self) -> float:
        return self.OLLAMA_TEMPERATURE

    @property
    def GROK_API_KEY(self) -> str:
        return self.GROQ_API_KEY

    @property
    def GROK_MODEL(self) -> str:
        return self.GROQ_MODEL

# Instantiate singleton settings to be imported across the app
settings = Settings()
