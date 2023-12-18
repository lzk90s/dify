from abc import ABC
from typing import Dict, Optional, Any

import openai
from pydantic import root_validator

from core.third_party.langchain.llms.azure_chat_open_ai import EnhanceAzureChatOpenAI


class TuyaHttpClient(openai.ChatCompletion, ABC):
    @classmethod
    def class_url(
            cls,
            engine: Optional[str] = None,
            api_type: Optional[str] = None,
            api_version: Optional[str] = None,
    ) -> str:
        return ''


class EnhanceTuyaChatAI(EnhanceAzureChatOpenAI):
    scene_id: str
    """scene id"""

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        try:
            values["client"] = TuyaHttpClient
        except AttributeError:
            raise ValueError(
                "`openai` has no `ChatCompletion` attribute, this is likely "
                "due to an old version of the openai package. Try upgrading it "
                "with `pip install --upgrade openai`."
            )
        if values["n"] < 1:
            raise ValueError("n must be at least 1.")
        if values["n"] > 1 and values["streaming"]:
            raise ValueError("n must be 1 when streaming.")
        return values

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        return {
            **super()._default_params,
            'sceneId': self.scene_id
        }
