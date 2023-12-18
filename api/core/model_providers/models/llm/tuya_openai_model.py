import logging
from typing import Any

import openai

from core.model_providers.error import LLMBadRequestError, LLMAPIConnectionError, LLMAPIUnavailableError, \
    LLMRateLimitError, LLMAuthorizationError
from core.model_providers.models.llm.azure_openai_model import AzureOpenAIModel
from core.third_party.langchain.llms.tuya_openai_llm import EnhanceTuyaChatAI

AZURE_OPENAI_API_VERSION = '2023-07-01-preview'


class TuyaOpenAIModel(AzureOpenAIModel):
    def _init_client(self) -> Any:
        provider_model_kwargs = self._to_model_kwargs_input(self.model_rules, self.model_kwargs)
        if self.name == 'text-davinci-003':
            raise NotImplementedError
        else:
            extra_model_kwargs = {
                'top_p': provider_model_kwargs.get('top_p'),
                'frequency_penalty': provider_model_kwargs.get('frequency_penalty'),
                'presence_penalty': provider_model_kwargs.get('presence_penalty'),
            }

            client = EnhanceTuyaChatAI(
                deployment_name=self.name,
                temperature=provider_model_kwargs.get('temperature'),
                max_tokens=provider_model_kwargs.get('max_tokens'),
                model_kwargs=extra_model_kwargs,
                streaming=self.streaming,
                request_timeout=60,
                openai_api_type='azure',
                openai_api_version=AZURE_OPENAI_API_VERSION,
                openai_api_key=self.credentials.get('openai_api_key'),
                openai_api_base=self.credentials.get('openai_api_base'),
                scene_id=self.credentials.get('scene_id'),
                callbacks=self.callbacks,
            )

        return client

    def handle_exceptions(self, ex: Exception) -> Exception:
        if isinstance(ex, openai.error.InvalidRequestError):
            logging.warning("Invalid request to Tuya OpenAI API.")
            return LLMBadRequestError(str(ex))
        elif isinstance(ex, openai.error.APIConnectionError):
            logging.warning("Failed to connect to Tuya OpenAI API.")
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
