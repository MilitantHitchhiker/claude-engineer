from ai_client_base import AIClient, Model
from config import Config, AIModelSelector
from anthropic import Anthropic
import openai
from groq import Groq

# Initialize Config
config = Config()

class AnthropicClient(AIClient):
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)

    def create_message(self, model, system, messages, tools=None, tool_choice=None):
        return self.client.messages.create(
            model=model.name,
            max_tokens=model.max_tokens,
            messages=[{"role": "system", "content": system}] + messages,
            tools=tools,
            tool_choice=tool_choice
        )

    def get_output_tokens(self, response):
        return response.usage.output_tokens if hasattr(response, 'usage') else 0

class OpenAIClient(AIClient):
    def __init__(self, api_key):
        openai.api_key = api_key

    def create_message(self, model, system, messages, tools=None, tool_choice=None):
        return openai.ChatCompletion.create(
            model=model.name,
            max_tokens=model.max_tokens,
            messages=[{"role": "system", "content": system}] + messages,
            tools=tools,
            tool_choice=tool_choice
        )

    def get_output_tokens(self, response):
        return response.usage.completion_tokens if hasattr(response, 'usage') else 0

class GroqClient(AIClient):
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def create_message(self, model, system, messages, tools=None, tool_choice=None):
        return self.client.chat.completions.create(
            model=model.name,
            max_tokens=model.max_tokens,
            messages=[{"role": "system", "content": system}] + messages,
            tools=tools,
            tool_choice=tool_choice
        )

    def get_output_tokens(self, response):
        return response.usage.completion_tokens if hasattr(response, 'usage') else 0

class AIClientFactory:
    _clients = {}

    @staticmethod
    def get_client(provider):
        if provider not in AIClientFactory._clients:
            api_key = config.valid_apis.get(provider)
            if provider == 'anthropic':
                AIClientFactory._clients[provider] = AnthropicClient(api_key)
            elif provider == 'openai':
                AIClientFactory._clients[provider] = OpenAIClient(api_key)
            elif provider == 'groq':
                AIClientFactory._clients[provider] = GroqClient(api_key)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        return AIClientFactory._clients[provider]
