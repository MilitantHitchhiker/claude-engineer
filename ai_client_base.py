from abc import ABC, abstractmethod

class Model:
    def __init__(self, name, provider, data):
        self.name = name
        self.provider = provider
        self.max_tokens = data['max_tokens']
        self.type = data['type']
        self.capabilities = data['capabilities']
        self.context_window = data['context_window']
        self.temperature = data['temperature']

class AIClient(ABC):
    @abstractmethod
    def create_message(self, model, system, messages, tools=None, tool_choice=None):
        pass

    @abstractmethod
    def get_output_tokens(self, response):
        pass