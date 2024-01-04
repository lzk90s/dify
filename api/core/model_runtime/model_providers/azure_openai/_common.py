import openai
from httpx import Timeout

from core.model_runtime.errors.invoke import InvokeConnectionError, InvokeServerUnavailableError, InvokeRateLimitError, \
    InvokeAuthorizationError, InvokeBadRequestError, InvokeError
from core.model_runtime.model_providers.azure_openai._constant import AZURE_OPENAI_API_VERSION


class _CommonAzureOpenAI:

    def build_client(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def _to_credential_kwargs(credentials: dict) -> dict:
        credentials_kwargs = {
            "api_key": credentials['openai_api_key'],
            "azure_endpoint": credentials['openai_api_base'],
            "api_version": AZURE_OPENAI_API_VERSION,
            "timeout": Timeout(315.0, read=300.0, write=10.0, connect=5.0),
            "max_retries": 1,
            'model': credentials.get('base_model_name').replace('gpt-35', 'gpt-3.5'),
        }

        return credentials_kwargs

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        return {
            InvokeConnectionError: [
                openai.APIConnectionError,
                openai.APITimeoutError
            ],
            InvokeServerUnavailableError: [
                openai.InternalServerError
            ],
            InvokeRateLimitError: [
                openai.RateLimitError
            ],
            InvokeAuthorizationError: [
                openai.AuthenticationError,
                openai.PermissionDeniedError
            ],
            InvokeBadRequestError: [
                openai.BadRequestError,
                openai.NotFoundError,
                openai.UnprocessableEntityError,
                openai.APIError
            ]
        }
