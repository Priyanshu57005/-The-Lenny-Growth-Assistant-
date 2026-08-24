import logging
from typing import Dict, Optional
from app.services.llm.base import BaseLLMProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.services.llm.anthropic_provider import AnthropicProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.config.settings import settings

logger = logging.getLogger("lenny_growth.llm.factory")

class LLMFactory:
    def __init__(self):
        self._active_provider_name = settings.LLM_PROVIDER.lower()
        self._providers: Dict[str, BaseLLMProvider] = {
            "ollama": OllamaProvider(),
            "anthropic": AnthropicProvider(),
            "openai": OpenAIProvider()
        }

    def get_provider(self, override_name: Optional[str] = None) -> BaseLLMProvider:
        target_name = (override_name or self._active_provider_name).lower()
        if target_name in self._providers:
            return self._providers[target_name]
        logger.warning(f"Unknown provider '{target_name}'. Falling back to Ollama.")
        return self._providers["ollama"]

    def set_active_provider(self, name: str) -> str:
        name = name.lower()
        if name in self._providers:
            self._active_provider_name = name
            logger.info(f"Active LLM provider switched to {name}")
            return name
        raise ValueError(f"Unsupported provider: {name}. Must be one of {list(self._providers.keys())}")

    @property
    def active_provider_name(self) -> str:
        return self._active_provider_name

    async def get_health_status(self) -> Dict[str, bool]:
        status = {}
        for name, provider in self._providers.items():
            status[name] = await provider.check_health()
        return status

    async def generate_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[list] = None,
        temperature: float = 0.7,
        provider_override: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generates response using configured primary LLM provider.
        If primary provider is unconfigured or unreachable, attempts failover to secondary configured cloud provider.
        If no healthy provider is available, raises structured diagnostic RuntimeError.
        """
        primary = self.get_provider(provider_override)
        try:
            res = await primary.generate(prompt, system_prompt, conversation_history, temperature)
            return res, primary.provider_name
        except Exception as primary_err:
            logger.warning(f"Primary provider '{primary.provider_name}' failed: {primary_err}. Trying configured cloud fallbacks...")
            
            # Order of fallbacks: Anthropic -> OpenAI -> Ollama
            fallback_order = ["anthropic", "openai", "ollama"]
            for fb_name in fallback_order:
                if fb_name == primary.provider_name:
                    continue
                fb_provider = self._providers[fb_name]
                if await fb_provider.check_health():
                    try:
                        logger.info(f"Failing over to healthy provider '{fb_name}'...")
                        res = await fb_provider.generate(prompt, system_prompt, conversation_history, temperature)
                        return res, fb_name
                    except Exception as fb_err:
                        logger.warning(f"Fallback provider '{fb_name}' failed: {fb_err}")

            # Structured error explaining exact diagnostic instructions for user & evaluator
            if primary.provider_name == "ollama":
                err_msg = (
                    f"Ollama Connection Error: Could not connect to local Ollama service at '{settings.OLLAMA_BASE_URL}'. "
                    f"Please ensure Ollama is installed and running (`ollama run {settings.OLLAMA_MODEL}`) or set ANTHROPIC_API_KEY / OPENAI_API_KEY in `.env`."
                )
            elif primary.provider_name == "anthropic":
                err_msg = "Anthropic API Error: Please verify ANTHROPIC_API_KEY is configured in your `.env` file or switch to Ollama."
            elif primary.provider_name == "openai":
                err_msg = "OpenAI API Error: Please verify OPENAI_API_KEY is configured in your `.env` file or switch to Ollama."
            else:
                err_msg = f"LLM Generation Error: {str(primary_err)}"

            raise RuntimeError(err_msg)

llm_factory = LLMFactory()
