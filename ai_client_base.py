from abc import ABC, abstractmethod
from typing import List, Dict

class Model:
    def __init__(self, name: str, provider: str, data: Dict[str, object]):
        self.name = name
        self.provider = provider
        self.max_tokens = data['max_tokens']
        self.type = data['type']
        self.capabilities = data['capabilities']
        self.context_window = data['context_window']
        self.temperature = data['temperature']

class AIClient(ABC):
    @abstractmethod
    def create_message(self, model: str, system: str, messages: List[Dict[str, str]], 
                       functions: List[Dict[str, object]] | None = None, 
                       function_call: str | None = None) -> object:
        pass

    @abstractmethod
    def get_output_tokens(self, response: object) -> int:
        pass

    @abstractmethod
    def execute_tool_calls(self, tool_calls: List[Dict[str, object]]) -> List[Dict[str, object]]:
        pass