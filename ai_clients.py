from ai_client_base import AIClient
from config import Config
from anthropic import Anthropic
import openai
from groq import Groq

# Initialize Config
config = Config()

class AnthropicClient(AIClient):
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)

    def create_message(self, model, system, messages, tools=None, tool_choice=None):
        model_data = config.get_model("text_models", "anthropic", model)
        return self.client.messages.create(
            model=model,
            max_tokens=model_data['max_tokens'],
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
        model_data = config.get_model("text_models", "openai", model)
        return openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=model_data['max_tokens'],
            tools=tools,
            tool_choice=tool_choice
        )

    def get_output_tokens(self, response):
        return response.usage.completion_tokens if hasattr(response, 'usage') else 0

class GroqClient(AIClient):
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        print(f"GroqClient initialized. Client type: {type(self.client)}")
        print(f"Client attributes: {dir(self.client)}")

    def create_message(self, model, system, messages, tools=None, tool_choice=None):
        print(f"GroqClient create_message called. Client type: {type(self.client)}")
        print(f"Client attributes: {dir(self.client)}")
        model_data = config.get_model("text_models", "groq", model)
        
        # Prepare messages in the correct format
        formatted_messages = [{"role": "system", "content": system}] + messages
        print(formatted_messages)

        response = self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            max_tokens=model_data['max_tokens'],
            #tools=tools,
            #tool_choice=tool_choice
        )
        return response

    def get_output_tokens(self, response):
        return response.usage.completion_tokens if hasattr(response, 'usage') else 0

class AIClientFactory:
    _clients = {}

    @staticmethod
    def get_client(provider):
        if provider not in AIClientFactory._clients:
            api_key = config.valid_apis.get(provider)
            if not api_key:
                raise ValueError(f"No API key found for provider: {provider}")
            
            if provider == "anthropic":
                AIClientFactory._clients[provider] = AnthropicClient(api_key)
            elif provider == "openai":
                AIClientFactory._clients[provider] = OpenAIClient(api_key)
            elif provider == "groq":
                api_key = config.valid_apis.get(provider)
                if not api_key:
                    raise ValueError(f"No API key found for provider: {provider}")
                AIClientFactory._clients[provider] = GroqClient(api_key)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        
        return AIClientFactory._clients[provider]

    @staticmethod
    def get_model(model_type: str, provider: str, model_name: str):
        return config.get_model(model_type, provider, model_name)