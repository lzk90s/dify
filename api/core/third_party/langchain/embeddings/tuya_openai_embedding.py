"""Wrapper around OpenLLM embedding models."""
from typing import Optional, Dict

import openai
import tiktoken
from langchain.embeddings import OpenAIEmbeddings, logger
from langchain.utils import get_from_dict_or_env
from openai import OpenAIError
from pydantic import root_validator


class TuyaHttpClient(openai.Embedding):
    @classmethod
    def class_url(
            cls,
            engine: Optional[str] = None,
            api_type: Optional[str] = None,
            api_version: Optional[str] = None,
    ) -> str:
        return ''

    @classmethod
    def create(cls, *args, **kwargs):
        model_name = kwargs.get("model")
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            logger.warning("Warning: model not found. Using cl100k_base encoding.")
            model = "cl100k_base"
            encoding = tiktoken.get_encoding(model)

        tokens = kwargs.pop("input")
        texts = [encoding.decode(t) for t in tokens]

        batch_prompt_tokens = 0
        batch_completion_tokens = 0
        batch_total_tokens = 0
        batch_data_list = []

        for text in texts:
            kwargs['input'] = text
            response = super().create(*args, **kwargs)
            if not response['success']:
                raise OpenAIError(
                    "Get embedding for {text} fail, error={error}, msg={msg}.".format(
                        text=kwargs['input'], error=response['errorCode'], msg=response['errorMessage']
                    )
                )
            original_data = response['data']
            usage = original_data['usage']
            if usage:
                batch_prompt_tokens += int(usage['prompt_tokens']) if usage['prompt_tokens'] else 0
                batch_completion_tokens += int(usage['completion_tokens']) if usage['completion_tokens'] else 0
                batch_total_tokens += int(usage['total_tokens']) if usage['total_tokens'] else 0
            batch_data_list += original_data['data']

        return {
            "object": "list",
            "model": "ada",
            "usage": {
                "prompt_tokens": str(batch_total_tokens),
                "completion_tokens": str(batch_completion_tokens),
                "total_tokens": str(batch_total_tokens),
            },
            "data": batch_data_list
        }


class EnhanceTuyaOpenAIEmbeddings(OpenAIEmbeddings):
    """Wrapper around OpenLLM embedding models.
    """

    scene_id: str = None
    """scene id"""

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        values["openai_api_key"] = get_from_dict_or_env(
            values, "openai_api_key", "OPENAI_API_KEY"
        )
        values["openai_api_base"] = get_from_dict_or_env(
            values,
            "openai_api_base",
            "OPENAI_API_BASE",
            default="",
        )
        values["openai_api_type"] = get_from_dict_or_env(
            values,
            "openai_api_type",
            "OPENAI_API_TYPE",
            default="",
        )
        values["openai_proxy"] = get_from_dict_or_env(
            values,
            "openai_proxy",
            "OPENAI_PROXY",
            default="",
        )
        if values["openai_api_type"] in ("azure", "azure_ad", "azuread"):
            default_api_version = "2022-12-01"
        else:
            default_api_version = ""
        values["openai_api_version"] = get_from_dict_or_env(
            values,
            "openai_api_version",
            "OPENAI_API_VERSION",
            default=default_api_version,
        )
        values["openai_organization"] = get_from_dict_or_env(
            values,
            "openai_organization",
            "OPENAI_ORGANIZATION",
            default="",
        )
        try:
            import openai

            values["client"] = TuyaHttpClient
        except ImportError:
            raise ImportError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )
        return values

    @property
    def _invocation_params(self) -> Dict:
        return {
            **super()._invocation_params,
            "engine": self.deployment,
            "encoding_format": "none",
            "sceneId": self.scene_id
        }
