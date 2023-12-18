import logging

import openai

from core.model_providers.error import LLMBadRequestError, LLMAuthorizationError, LLMRateLimitError, \
    LLMAPIUnavailableError, LLMAPIConnectionError
from core.model_providers.models.embedding.azure_openai_embedding import AZURE_OPENAI_API_VERSION
from core.model_providers.models.embedding.base import BaseEmbedding
from core.model_providers.providers.base import BaseModelProvider
from core.third_party.langchain.embeddings.tuya_openai_embedding import EnhanceTuyaOpenAIEmbeddings


class TuyaOpenAIEmbedding(BaseEmbedding):
    def __init__(self, model_provider: BaseModelProvider, name: str):
        self.credentials = model_provider.get_model_credentials(
            model_name=name,
            model_type=self.type
        )

        client = EnhanceTuyaOpenAIEmbeddings(
            deployment=name,
            openai_api_type='azure',
            openai_api_version=AZURE_OPENAI_API_VERSION,
            chunk_size=16,
            max_retries=1,
            openai_api_key=self.credentials.get('openai_api_key'),
            openai_api_base=self.credentials.get('openai_api_base')
        )

        super().__init__(model_provider, client, name)

    def handle_exceptions(self, ex: Exception) -> Exception:
        if isinstance(ex, openai.error.InvalidRequestError):
            logging.warning("Invalid request to Azure OpenAI API.")
            return LLMBadRequestError(str(ex))
        elif isinstance(ex, openai.error.APIConnectionError):
            logging.warning("Failed to connect to Azure OpenAI API.")
            return LLMAPIConnectionError(ex.__class__.__name__ + ":" + str(ex))
        elif isinstance(ex, (openai.error.APIError, openai.error.ServiceUnavailableError, openai.error.Timeout)):
            logging.warning("Azure OpenAI service unavailable.")
            return LLMAPIUnavailableError(ex.__class__.__name__ + ":" + str(ex))
        elif isinstance(ex, openai.error.RateLimitError):
            return LLMRateLimitError('Azure ' + str(ex))
        elif isinstance(ex, openai.error.AuthenticationError):
            return LLMAuthorizationError('Azure ' + str(ex))
        elif isinstance(ex, openai.error.OpenAIError):
            return LLMBadRequestError('Azure ' + ex.__class__.__name__ + ":" + str(ex))
        else:
            return ex
