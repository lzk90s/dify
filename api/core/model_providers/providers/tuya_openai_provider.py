import json
import logging
from typing import Type

import openai
from langchain.schema import HumanMessage

from core.model_providers.models.base import BaseProviderModel
from core.model_providers.models.embedding.azure_openai_embedding import AZURE_OPENAI_API_VERSION
from core.model_providers.models.embedding.tuya_openai_embedding import TuyaOpenAIEmbedding
from core.model_providers.models.entity.model_params import ModelType
from core.model_providers.models.llm.tuya_openai_model import TuyaOpenAIModel
from core.model_providers.providers.azure_openai_provider import AzureOpenAIProvider, BASE_MODELS
from core.model_providers.providers.base import CredentialsValidateFailedError
from core.model_providers.providers.hosted import hosted_model_providers
from core.third_party.langchain.embeddings.tuya_openai_embedding import EnhanceTuyaOpenAIEmbeddings
from core.third_party.langchain.llms.tuya_openai_llm import EnhanceTuyaChatAI
from models.provider import ProviderType


class TuyaOpenAIProvider(AzureOpenAIProvider):

    @property
    def provider_name(self):
        """
        Returns the name of a provider.
        """
        return 'tuya_openai'

    def get_model_class(self, model_type: ModelType) -> Type[BaseProviderModel]:
        """
        Returns the model class.

        :param model_type:
        :return:
        """
        if model_type == ModelType.TEXT_GENERATION:
            model_class = TuyaOpenAIModel
        elif model_type == ModelType.EMBEDDINGS:
            model_class = TuyaOpenAIEmbedding
        else:
            raise NotImplementedError

        return model_class

    @classmethod
    def encrypt_provider_credentials(cls, tenant_id: str, credentials: dict) -> dict:
        return credentials

    @classmethod
    def is_model_credentials_valid_or_raise(cls, model_name: str, model_type: ModelType, credentials: dict):
        """
        check model credentials valid.

        :param model_name:
        :param model_type:
        :param credentials:
        """
        if 'openai_api_key' not in credentials:
            raise CredentialsValidateFailedError('Azure OpenAI API key is required')

        if 'openai_api_base' not in credentials:
            raise CredentialsValidateFailedError('Azure OpenAI API Base Endpoint is required')

        if 'base_model_name' not in credentials:
            raise CredentialsValidateFailedError('Base Model Name is required')

        if credentials['base_model_name'] not in BASE_MODELS:
            raise CredentialsValidateFailedError('Base Model Name is invalid')

        if model_type == ModelType.TEXT_GENERATION:
            try:
                client = EnhanceTuyaChatAI(
                    deployment_name=model_name,
                    temperature=0,
                    max_tokens=15,
                    request_timeout=10,
                    openai_api_type='azure',
                    openai_api_version='2023-07-01-preview',
                    openai_api_key=credentials['openai_api_key'],
                    openai_api_base=credentials['openai_api_base'],
                    scene_id=credentials.get('scene_id'),
                )

                client.generate([[HumanMessage(content='hi!')]])
            except openai.error.OpenAIError as e:
                raise CredentialsValidateFailedError(
                    f"Azure OpenAI deployment {model_name} not exists, cause: {e.__class__.__name__}:{str(e)}")
            except Exception as e:
                logging.exception("Azure OpenAI Model retrieve failed.")
                raise e
        elif model_type == ModelType.EMBEDDINGS:
            try:
                client = EnhanceTuyaOpenAIEmbeddings(
                    openai_api_type='azure',
                    openai_api_version=AZURE_OPENAI_API_VERSION,
                    deployment=model_name,
                    chunk_size=16,
                    max_retries=1,
                    openai_api_key=credentials['openai_api_key'],
                    openai_api_base=credentials['openai_api_base'],
                    scene_id=credentials.get('scene_id'),
                )

                client.embed_query('hi')
            except openai.error.OpenAIError as e:
                logging.exception("Azure OpenAI Model check error.")
                raise CredentialsValidateFailedError(
                    f"Azure OpenAI deployment {model_name} not exists, cause: {e.__class__.__name__}:{str(e)}")
            except Exception as e:
                logging.exception("Azure OpenAI Model retrieve failed.")
                raise e

    def get_model_credentials(self, model_name: str, model_type: ModelType, obfuscated: bool = False) -> dict:
        """
        get credentials for llm use.

        :param model_name:
        :param model_type:
        :param obfuscated:
        :return:
        """
        if self.provider.provider_type == ProviderType.CUSTOM.value:
            # convert old provider config to provider models
            self._convert_provider_config_to_model_config()

            provider_model = self._get_provider_model(model_name, model_type)

            if not provider_model.encrypted_config:
                return {
                    'openai_api_base': '',
                    'openai_api_key': '',
                    'base_model_name': '',
                    'scene_id': '',
                }

            credentials = json.loads(provider_model.encrypted_config)
            return {
                'openai_api_base': credentials['openai_api_base'],
                'openai_api_key': credentials['openai_api_key'],
                'base_model_name': credentials['base_model_name'],
                'scene_id': credentials['scene_id'],
            }
        else:
            if hosted_model_providers.azure_openai:
                return {
                    'openai_api_base': hosted_model_providers.azure_openai.api_base,
                    'openai_api_key': hosted_model_providers.azure_openai.api_key,
                    'base_model_name': model_name,
                    'scene_id': None
                }
            else:
                return {
                    'openai_api_base': None,
                    'openai_api_key': None,
                    'base_model_name': None,
                    'scene_id': None
                }
