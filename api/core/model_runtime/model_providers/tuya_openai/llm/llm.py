import logging

from core.model_runtime.errors.validate import CredentialsValidateFailedError
from core.model_runtime.model_providers.azure_openai.llm.llm import AzureOpenAILargeLanguageModel
from core.model_runtime.model_providers.tuya_openai._common import _CommonTuyaOpenAI
from core.model_runtime.model_providers.tuya_openai.client import TuyaOpenAIClient

logger = logging.getLogger(__name__)


class TuyaOpenAILargeLanguageModel(AzureOpenAILargeLanguageModel, _CommonTuyaOpenAI):

    def build_client(self, *args, **kwargs):
        return TuyaOpenAIClient()

    def validate_credentials(self, model: str, credentials: dict) -> None:
        if 'scene_id' not in credentials:
            raise CredentialsValidateFailedError('Azure OpenAI API Base Endpoint is required')

        super().validate_credentials(model, credentials)
