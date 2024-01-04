import logging

from core.model_runtime.model_providers.azure_openai.azure_openai import AzureOpenAIProvider

logger = logging.getLogger(__name__)


class TuyaOpenAIProvider(AzureOpenAIProvider):

    def validate_provider_credentials(self, credentials: dict) -> None:
        pass
