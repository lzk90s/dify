"""Wrapper around OpenLLM embedding models."""
from typing import Optional

import openai
from langchain.embeddings import OpenAIEmbeddings


class TuyaHttpClient(openai.Embedding):
    @classmethod
    def class_url(
            cls,
            engine: Optional[str] = None,
            api_type: Optional[str] = None,
            api_version: Optional[str] = None,
    ) -> str:
        return ''


class EnhanceTuyaOpenAIEmbeddings(OpenAIEmbeddings):
    """Wrapper around OpenLLM embedding models.
    """
    pass
