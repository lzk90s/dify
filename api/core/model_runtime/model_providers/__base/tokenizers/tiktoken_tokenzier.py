from threading import Lock
from typing import Any

import tiktoken

_tokenizer = None
_lock = Lock()


class TikTokenTokenizer:
    @staticmethod
    def _get_num_tokens_by_tiktoken(text: str) -> int:
        """
            use gpt2 tokenizer to get num tokens
        """
        _tokenizer = TikTokenTokenizer.get_encoder()
        tokens = _tokenizer.encode(text)
        return len(tokens)

    @staticmethod
    def get_num_tokens(text: str) -> int:
        return TikTokenTokenizer._get_num_tokens_by_tiktoken(text)

    @staticmethod
    def get_encoder() -> Any:
        global _tokenizer, _lock
        with _lock:
            _tokenizer = tiktoken.get_encoding("cl100k_base")
            return _tokenizer
