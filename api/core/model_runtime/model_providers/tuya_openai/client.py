import logging

import tiktoken
from openai.lib.azure import AzureOpenAI
from openai.resources import Embeddings
from openai.resources.chat import Completions, Chat


class TuyaOpenAIChatCompletions(Completions):
    @classmethod
    def create(cls, *args, **kwargs):
        response = super().create(*args, **kwargs)
        return response['data'] if isinstance(response, dict) and 'errorCode' in response else response


class TuyaOpenAIChat(Chat):
    def __init__(self, client) -> None:
        super().__init__(client)
        self.completions = TuyaOpenAIChatCompletions(client)

    @classmethod
    def create(cls, *args, **kwargs):
        response = super().create(*args, **kwargs)
        return response['data'] if isinstance(response, dict) and 'errorCode' in response else response


class TuyaOpenAIEmbeddings(Embeddings):
    logger = logging.getLogger(__name__)

    @classmethod
    def create(cls, *args, **kwargs):
        model_name = kwargs.get("model")
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            cls.logger.warning("Warning: model not found. Using cl100k_base encoding.")
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
                raise Exception(
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


class TuyaOpenAIClient(AzureOpenAI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat = TuyaOpenAIChat(self)
        self.embeddings = TuyaOpenAIEmbeddings(self)

#
# class EnhanceTuyaChatAI(AzureOpenAI):
#     scene_id: str
#     """scene id"""
#
#     @root_validator()
#     def validate_environment(cls, values: Dict) -> Dict:
#         """Validate that api key and python package exists in environment."""
#         try:
#             values["client"] = TuyaHttpClient
#         except AttributeError:
#             raise ValueError(
#                 "`openai` has no `ChatCompletion` attribute, this is likely "
#                 "due to an old version of the openai package. Try upgrading it "
#                 "with `pip install --upgrade openai`."
#             )
#         if values["n"] < 1:
#             raise ValueError("n must be at least 1.")
#         if values["n"] > 1 and values["streaming"]:
#             raise ValueError("n must be 1 when streaming.")
#         return values
#
#     @property
#     def _default_params(self) -> Dict[str, Any]:
#         """Get the default parameters for calling OpenAI API."""
#         return {
#             **super()._default_params,
#             'sceneId': self.scene_id,
#             'maxTokens': self.max_tokens,
#         }
