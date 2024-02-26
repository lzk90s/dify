import json
import logging
from collections.abc import Generator
from typing import Optional, Union, cast
from urllib.parse import urljoin

import requests

from core.model_runtime.entities.common_entities import I18nObject
from core.model_runtime.entities.llm_entities import LLMMode, LLMResult, LLMResultChunk, LLMResultChunkDelta
from core.model_runtime.entities.message_entities import (
    AssistantPromptMessage,
    ImagePromptMessageContent,
    PromptMessage,
    PromptMessageContent,
    PromptMessageContentType,
    PromptMessageFunction,
    PromptMessageTool,
    SystemPromptMessage,
    ToolPromptMessage,
    UserPromptMessage,
)
from core.model_runtime.entities.model_entities import (
    AIModelEntity,
    FetchFrom,
    ModelType,
)
from core.model_runtime.errors.invoke import InvokeError
from core.model_runtime.errors.validate import CredentialsValidateFailedError
from core.model_runtime.model_providers.__base.large_language_model import LargeLanguageModel
from core.model_runtime.model_providers.openai_api_compatible._common import _CommonOAI_API_Compat
from core.model_runtime.utils import helper

logger = logging.getLogger(__name__)


class OAIAPICompatLargeLanguageModel(_CommonOAI_API_Compat, LargeLanguageModel):
    """
    Model class for OpenAI large language model.
    """

    def _invoke(self, model: str, credentials: dict,
                prompt_messages: list[PromptMessage], model_parameters: dict,
                tools: Optional[list[PromptMessageTool]] = None, stop: Optional[list[str]] = None,
                stream: bool = True, user: Optional[str] = None) \
            -> Union[LLMResult, Generator]:
        """
        Invoke large language model

        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """

        # text completion model
        return self._generate(
            model=model,
            credentials=credentials,
            prompt_messages=prompt_messages,
            model_parameters=model_parameters,
            tools=tools,
            stop=stop,
            stream=stream,
            user=user
        )

    def get_num_tokens(self, model: str, credentials: dict, prompt_messages: list[PromptMessage],
                       tools: Optional[list[PromptMessageTool]] = None) -> int:
        """
        Get number of tokens for given prompt messages

        :param model:
        :param credentials:
        :param prompt_messages:
        :param tools: tools for tool calling
        :return:
        """
        return self._num_tokens_from_messages(model, prompt_messages, tools)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials using requests to ensure compatibility with all providers following OpenAI's API standard.

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            headers = {
                'Content-Type': 'application/json; charset=utf-8'
            }

            api_key = credentials.get('api_key')
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            endpoint_url = credentials['endpoint_url']
            if not endpoint_url.endswith('/'):
                endpoint_url += '/'

            # prepare the payload for a simple ping to the model
            data = {
                'model': model,
                'max_tokens': 5,
                'sceneId': api_key,
                'stream': False
            }

            completion_type = LLMMode.value_of(credentials['mode'])

            if completion_type is LLMMode.CHAT:
                data['messages'] = [
                    {
                        "role": "user",
                        "content": "ping"
                    },
                ]
                endpoint_url = urljoin(endpoint_url, 'chat')
            elif completion_type is LLMMode.COMPLETION:
                data['prompt'] = 'ping'
                endpoint_url = urljoin(endpoint_url, 'completions')
            else:
                raise ValueError("Unsupported completion type for model configuration.")

            # send a post request to validate the credentials
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=data,
                timeout=(10, 60),
                verify=False
            )
            response.encoding = 'utf-8'

            if response.status_code != 200:
                raise CredentialsValidateFailedError(
                    f'Credentials validation failed with status code {response.status_code}')

            try:
                json_result = response.json()
                if json_result['errorCode']:
                    raise CredentialsValidateFailedError(
                        f'Credentials validation failed: http error {json_result["errorMessage"]}')
                json_result = json_result['data']
            except json.JSONDecodeError as e:
                raise CredentialsValidateFailedError('Credentials validation failed: JSON decode error')

            if (completion_type is LLMMode.CHAT
                    and ('object' not in json_result or json_result['object'] != 'chat.completion')):
                raise CredentialsValidateFailedError(
                    'Credentials validation failed: invalid response object, must be \'chat.completion\'')
            elif (completion_type is LLMMode.COMPLETION
                  and ('object' not in json_result or json_result['object'] != 'text_completion')):
                raise CredentialsValidateFailedError(
                    'Credentials validation failed: invalid response object, must be \'text_completion\'')
        except CredentialsValidateFailedError:
            raise
        except Exception as ex:
            raise CredentialsValidateFailedError(f'An error occurred during credentials validation: {str(ex)}')

    def get_customizable_model_schema(self, model: str, credentials: dict) -> AIModelEntity:
        """
            generate custom model entities from credentials
        """
        if not model.startswith('ft:'):
            base_model = model
        else:
            # get base_model
            base_model = model.split(':')[1]

        # get model schema
        models = self.predefined_models()
        model_map = {model.model: model for model in models}
        if base_model not in model_map:
            raise ValueError(f'Base model {base_model} not found')

        base_model_schema = model_map[base_model]

        base_model_schema_features = base_model_schema.features or []
        base_model_schema_model_properties = base_model_schema.model_properties or {}
        base_model_schema_parameters_rules = base_model_schema.parameter_rules or []

        entity = AIModelEntity(
            model=model,
            label=I18nObject(
                zh_Hans=model,
                en_US=model
            ),
            model_type=ModelType.LLM,
            features=[feature for feature in base_model_schema_features],
            fetch_from=FetchFrom.CUSTOMIZABLE_MODEL,
            model_properties={
                key: property for key, property in base_model_schema_model_properties.items()
            },
            parameter_rules=[rule for rule in base_model_schema_parameters_rules],
            pricing=base_model_schema.pricing
        )

        return entity

    # validate_credentials method has been rewritten to use the requests library for compatibility with all providers following OpenAI's API standard.
    def _generate(self, model: str, credentials: dict, prompt_messages: list[PromptMessage], model_parameters: dict,
                  tools: Optional[list[PromptMessageTool]] = None, stop: Optional[list[str]] = None,
                  stream: bool = True, \
                  user: Optional[str] = None) -> Union[LLMResult, Generator]:
        """
        Invoke llm completion model

        :param model: model name
        :param credentials: credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Charset': 'utf-8',
        }

        api_key = credentials.get('api_key')
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        endpoint_url = credentials["endpoint_url"]
        if not endpoint_url.endswith('/'):
            endpoint_url += '/'

        data = {
            "model": model,
            "stream": stream,
            "sceneId": api_key,
            **model_parameters
        }

        if 'mode' not in credentials:
            credentials['mode'] = 'chat'

        completion_type = LLMMode.value_of(credentials['mode'])

        if completion_type is LLMMode.CHAT:
            endpoint_url = urljoin(endpoint_url, 'chat')
            data['messages'] = [self._convert_prompt_message_to_dict(m) for m in prompt_messages]
        elif completion_type is LLMMode.COMPLETION:
            endpoint_url = urljoin(endpoint_url, 'completions')
            data['prompt'] = prompt_messages[0].content
        else:
            raise ValueError("Unsupported completion type for model configuration.")

        # annotate tools with names, descriptions, etc.
        formatted_tools = []
        if tools:
            data["tool_choice"] = "auto"

            for tool in tools:
                formatted_tools.append(helper.dump_model(PromptMessageFunction(function=tool)))

            data["tools"] = formatted_tools

        if stop:
            data["stop"] = stop

        if user:
            data["user"] = user

        response = requests.post(
            endpoint_url,
            headers=headers,
            json=data,
            timeout=(10, 60),
            stream=stream,
            verify=False
        )
        response.encoding = 'utf-8'

        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = 'utf-8'

        if response.status_code != 200:
            raise InvokeError(f"API request failed with status code {response.status_code}: {response.text}")

        if stream:
            return self._handle_generate_stream_response(model, credentials, response, prompt_messages)

        return self._handle_generate_response(model, credentials, response, prompt_messages)

    def _handle_generate_stream_response(self, model: str, credentials: dict, response: requests.Response,
                                         prompt_messages: list[PromptMessage]) -> Generator:
        """
        Handle llm stream response

        :param model: model name
        :param credentials: model credentials
        :param response: streamed response
        :param prompt_messages: prompt messages
        :return: llm response chunk generator
        """
        full_assistant_content = ''
        chunk_index = 0

        def create_final_llm_result_chunk(index: int, message: AssistantPromptMessage, finish_reason: str) \
                -> LLMResultChunk:
            # calculate num tokens
            prompt_tokens = self._num_tokens_from_string(model, prompt_messages[0].content)
            completion_tokens = self._num_tokens_from_string(model, full_assistant_content)

            # transform usage
            usage = self._calc_response_usage(model, credentials, prompt_tokens, completion_tokens)

            return LLMResultChunk(
                model=model,
                prompt_messages=prompt_messages,
                delta=LLMResultChunkDelta(
                    index=index,
                    message=message,
                    finish_reason=finish_reason,
                    usage=usage
                )
            )

        # delimiter for stream response, need unicode_escape
        import codecs
        delimiter = credentials.get("stream_mode_delimiter", "\n\n")
        delimiter = codecs.decode(delimiter, "unicode_escape")

        for chunk in response.iter_lines(decode_unicode=True, delimiter=delimiter):
            if chunk:
                # ignore sse comments
                if chunk.startswith(':'):
                    continue
                decoded_chunk = chunk.strip().lstrip('data: ').lstrip()
                chunk_json = None
                try:
                    chunk_json = json.loads(decoded_chunk)
                # stream ended
                except json.JSONDecodeError as e:
                    yield create_final_llm_result_chunk(
                        index=chunk_index + 1,
                        message=AssistantPromptMessage(content=""),
                        finish_reason="Non-JSON encountered."
                    )
                    break
                if not chunk_json or len(chunk_json['choices']) == 0:
                    continue

                choice = chunk_json['choices'][0]
                finish_reason = chunk_json['choices'][0].get('finish_reason')
                chunk_index += 1

                if 'delta' in choice:
                    delta = choice['delta']
                    delta_content = delta.get('content')

                    assistant_message_tool_calls = delta.get('tool_calls', None)
                    # assistant_message_function_call = delta.delta.function_call

                    if (delta_content is None or delta_content == '') and not assistant_message_tool_calls:
                        continue

                    # extract tool calls from response
                    tool_calls = []
                    if assistant_message_tool_calls:
                        tool_calls = self._extract_response_tool_calls(assistant_message_tool_calls)
                    # function_call = self._extract_response_function_call(assistant_message_function_call)
                    # tool_calls = [function_call] if function_call else []

                    # transform assistant message to prompt message
                    if delta_content is None:
                        delta_content = ''

                    assistant_prompt_message = AssistantPromptMessage(
                        content=delta_content,
                        tool_calls=tool_calls if assistant_message_tool_calls else []
                    )

                    full_assistant_content += delta_content
                elif 'text' in choice:
                    choice_text = choice.get('text', '')
                    if choice_text == '':
                        continue

                    # transform assistant message to prompt message
                    assistant_prompt_message = AssistantPromptMessage(content=choice_text)
                    full_assistant_content += choice_text
                else:
                    continue

                # check payload indicator for completion
                if finish_reason is not None:
                    yield create_final_llm_result_chunk(
                        index=chunk_index,
                        message=assistant_prompt_message,
                        finish_reason=finish_reason
                    )
                else:
                    yield LLMResultChunk(
                        model=model,
                        prompt_messages=prompt_messages,
                        delta=LLMResultChunkDelta(
                            index=chunk_index,
                            message=assistant_prompt_message,
                        )
                    )

            chunk_index += 1

    def _handle_generate_response(self, model: str, credentials: dict, response: requests.Response,
                                  prompt_messages: list[PromptMessage]) -> LLMResult:

        raw_response = response.json()
        if 'errorCode' in raw_response and raw_response['errorCode'] and raw_response['errorCode'] != '200':
            raise InvokeError(
                f"API request failed with status code {raw_response['errorCode']}: {raw_response['errorMessage']}")

        response_json = raw_response['data'] if 'data' in raw_response else raw_response

        completion_type = LLMMode.value_of(credentials['mode'])

        output = response_json['choices'][0]

        response_content = ''
        tool_calls = None

        if completion_type is LLMMode.CHAT:
            response_content = output.get('message', {})['content']
            tool_calls = output.get('message', {}).get('tool_calls')

        elif completion_type is LLMMode.COMPLETION:
            response_content = output['text']

        assistant_message = AssistantPromptMessage(content=response_content, tool_calls=[])

        if tool_calls:
            assistant_message.tool_calls = self._extract_response_tool_calls(tool_calls)

        usage = response_json.get("usage")
        if usage:
            # transform usage
            prompt_tokens = int(usage["prompt_tokens"])
            completion_tokens = int(usage["completion_tokens"])
        else:
            # calculate num tokens
            prompt_tokens = self._num_tokens_from_string(model, prompt_messages[0].content)
            completion_tokens = self._num_tokens_from_string(model, assistant_message.content)

        # transform usage
        usage = self._calc_response_usage(model, credentials, prompt_tokens, completion_tokens)

        # transform response
        result = LLMResult(
            model=response_json["model"],
            prompt_messages=prompt_messages,
            message=assistant_message,
            usage=usage,
        )

        return result

    def _convert_prompt_message_to_dict(self, message: PromptMessage) -> dict:
        """
        Convert PromptMessage to dict for OpenAI API format
        """
        if isinstance(message, UserPromptMessage):
            message = cast(UserPromptMessage, message)
            if isinstance(message.content, str):
                message_dict = {"role": "user", "content": message.content}
            else:
                sub_messages = []
                for message_content in message.content:
                    if message_content.type == PromptMessageContentType.TEXT:
                        message_content = cast(PromptMessageContent, message_content)
                        sub_message_dict = {
                            "type": "text",
                            "text": message_content.data
                        }
                        sub_messages.append(sub_message_dict)
                    elif message_content.type == PromptMessageContentType.IMAGE:
                        message_content = cast(ImagePromptMessageContent, message_content)
                        sub_message_dict = {
                            "type": "image_url",
                            "image_url": {
                                "url": message_content.data,
                                "detail": message_content.detail.value
                            }
                        }
                        sub_messages.append(sub_message_dict)

                message_dict = {"role": "user", "content": sub_messages}
        elif isinstance(message, AssistantPromptMessage):
            message = cast(AssistantPromptMessage, message)
            message_dict = {"role": "assistant", "content": message.content}
            if message.tool_calls:
                # message_dict["tool_calls"] = [helper.dump_model(PromptMessageFunction(function=tool_call)) for tool_call
                #                               in
                #                               message.tool_calls]
                function_calls = message.tool_calls
                message_dict["toolCalls"] = [
                    {
                        "type": "function",
                        "id": function_call.id,
                        "function": {
                            "name": function_call.function.name,
                            "arguments": function_call.function.arguments,
                        }
                    } for function_call in function_calls
                ]
        elif isinstance(message, SystemPromptMessage):
            message = cast(SystemPromptMessage, message)
            message_dict = {"role": "system", "content": message.content}
        elif isinstance(message, ToolPromptMessage):
            message = cast(ToolPromptMessage, message)
            message_dict = {
                "role": "tool",
                "content": message.content,
                "toolCallId": message.tool_call_id
            }
            # message_dict = {
            #     "role": "function",
            #     "content": message.content,
            #     "name": message.tool_call_id
            # }
        else:
            raise ValueError(f"Got unknown type {message}")

        if message.name is not None:
            message_dict["name"] = message.name

        return message_dict

    def _num_tokens_from_string(self, model: str, text: str,
                                tools: Optional[list[PromptMessageTool]] = None) -> int:
        """
        Approximate num tokens for model with gpt2 tokenizer.

        :param model: model name
        :param text: prompt text
        :param tools: tools for tool calling
        :return: number of tokens
        """
        num_tokens = self._get_num_tokens_by_gpt2(text)

        if tools:
            num_tokens += self._num_tokens_for_tools(tools)

        return num_tokens

    def _num_tokens_from_messages(self, model: str, messages: list[PromptMessage],
                                  tools: Optional[list[PromptMessageTool]] = None) -> int:
        """
        Approximate num tokens with GPT2 tokenizer.
        """

        tokens_per_message = 3
        tokens_per_name = 1

        num_tokens = 0
        messages_dict = [self._convert_prompt_message_to_dict(m) for m in messages]
        for message in messages_dict:
            num_tokens += tokens_per_message
            for key, value in message.items():
                # Cast str(value) in case the message value is not a string
                # This occurs with function messages
                # TODO: The current token calculation method for the image type is not implemented,
                #  which need to download the image and then get the resolution for calculation,
                #  and will increase the request delay
                if isinstance(value, list):
                    text = ''
                    for item in value:
                        if isinstance(item, dict) and item['type'] == 'text':
                            text += item['text']

                    value = text

                if key == "tool_calls":
                    for tool_call in value:
                        for t_key, t_value in tool_call.items():
                            num_tokens += self._get_num_tokens_by_gpt2(t_key)
                            if t_key == "function":
                                for f_key, f_value in t_value.items():
                                    num_tokens += self._get_num_tokens_by_gpt2(f_key)
                                    num_tokens += self._get_num_tokens_by_gpt2(f_value)
                            else:
                                num_tokens += self._get_num_tokens_by_gpt2(t_key)
                                num_tokens += self._get_num_tokens_by_gpt2(t_value)
                else:
                    num_tokens += self._get_num_tokens_by_gpt2(str(value))

                if key == "name":
                    num_tokens += tokens_per_name

        # every reply is primed with <im_start>assistant
        num_tokens += 3

        if tools:
            num_tokens += self._num_tokens_for_tools(tools)

        return num_tokens

    def _num_tokens_for_tools(self, tools: list[PromptMessageTool]) -> int:
        """
        Calculate num tokens for tool calling with tiktoken package.

        :param tools: tools for tool calling
        :return: number of tokens
        """
        num_tokens = 0
        for tool in tools:
            num_tokens += self._get_num_tokens_by_gpt2('type')
            num_tokens += self._get_num_tokens_by_gpt2('function')
            num_tokens += self._get_num_tokens_by_gpt2('function')

            # calculate num tokens for function object
            num_tokens += self._get_num_tokens_by_gpt2('name')
            num_tokens += self._get_num_tokens_by_gpt2(tool.name)
            num_tokens += self._get_num_tokens_by_gpt2('description')
            num_tokens += self._get_num_tokens_by_gpt2(tool.description)
            parameters = tool.parameters
            num_tokens += self._get_num_tokens_by_gpt2('parameters')
            if 'title' in parameters:
                num_tokens += self._get_num_tokens_by_gpt2('title')
                num_tokens += self._get_num_tokens_by_gpt2(parameters.get("title"))
            num_tokens += self._get_num_tokens_by_gpt2('type')
            num_tokens += self._get_num_tokens_by_gpt2(parameters.get("type"))
            if 'properties' in parameters:
                num_tokens += self._get_num_tokens_by_gpt2('properties')
                for key, value in parameters.get('properties').items():
                    num_tokens += self._get_num_tokens_by_gpt2(key)
                    for field_key, field_value in value.items():
                        num_tokens += self._get_num_tokens_by_gpt2(field_key)
                        if field_key == 'enum':
                            for enum_field in field_value:
                                num_tokens += 3
                                num_tokens += self._get_num_tokens_by_gpt2(enum_field)
                        else:
                            num_tokens += self._get_num_tokens_by_gpt2(field_key)
                            num_tokens += self._get_num_tokens_by_gpt2(str(field_value))
            if 'required' in parameters:
                num_tokens += self._get_num_tokens_by_gpt2('required')
                for required_field in parameters['required']:
                    num_tokens += 3
                    num_tokens += self._get_num_tokens_by_gpt2(required_field)

        return num_tokens

    def _extract_response_tool_calls(self,
                                     response_tool_calls: list[dict]) \
            -> list[AssistantPromptMessage.ToolCall]:
        """
        Extract tool calls from response

        :param response_tool_calls: response tool calls
        :return: list of tool calls
        """
        tool_calls = []
        if response_tool_calls:
            for response_tool_call in response_tool_calls:
                if 'function' not in response_tool_call or 'name' not in response_tool_call['function']:
                    continue

                function = AssistantPromptMessage.ToolCall.ToolCallFunction(
                    name=response_tool_call["function"]["name"],
                    arguments=response_tool_call["function"]["arguments"]
                )

                tool_call = AssistantPromptMessage.ToolCall(
                    id=response_tool_call["id"],
                    type=response_tool_call["type"],
                    function=function
                )
                tool_calls.append(tool_call)

        return tool_calls
