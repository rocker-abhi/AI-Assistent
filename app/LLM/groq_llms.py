from app.LLM.assistant import Assistant as UnifiedAssistant
from app.core.config import settings

class Assistant(UnifiedAssistant):
    def __init__(self, model_name=None, temperature=None, voice=None, rate=None):
        super().__init__(
            provider="groq",
            model_name=model_name or settings.GROQ_MODEL,
            temperature=temperature if temperature is not None else settings.GROQ_TEMPERATURE,
            voice=voice,
            rate=rate
        )
