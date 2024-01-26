from core.tools.entities.user_entities import UserToolProvider
from typing import List

position = {
    'google': 1,
    'wikipedia': 2,
    'dalle': 3,
    'webscraper': 4,
    'wolframalpha': 5,
    'chart': 6,
    'time': 7,
    'yahoo': 8,
    'stablediffusion': 9,
    'vectorizer': 10,
    'youtube': 11,
}

class BuiltinToolProviderSort:
    @staticmethod
    def sort(providers: List[UserToolProvider]) -> List[UserToolProvider]:
        def sort_compare(provider: UserToolProvider) -> int:
            return position.get(provider.name, 10000)
        
        sorted_providers = sorted(providers, key=sort_compare)

        return sorted_providers