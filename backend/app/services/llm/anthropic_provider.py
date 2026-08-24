import logging
from typing import List, Dict, Optional
import anthropic
from app.services.llm.base import BaseLLMProvider
from app.config.settings import settings

logger = logging.getLogger("lenny_growth.llm.anthropic")

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self._model = model or settings.ANTHROPIC_MODEL
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key) if self.api_key else None

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def model_name(self) -> str:
        return self._model

    async def check_health(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7
    ) -> str:
        if not self.client:
            raise RuntimeError("Anthropic API key is not configured.")

        messages = []
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self._model,
            "max_tokens": 4096,
            "messages": messages,
            "temperature": temperature
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        try:
            response = await self.client.messages.create(**kwargs)
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return ""
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise RuntimeError(f"Anthropic API call failed: {str(e)}")
