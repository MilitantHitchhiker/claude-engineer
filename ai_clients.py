from ai_client_base import AIClient
from config import Config
from anthropic import Anthropic
import openai
from groq import Groq
from typing import List, Dict
import json

# Initialize Config
config = Config()

class AnthropicClient:
    """
    A client for interacting with the Anthropic API.
    """

    def __init__(self, api_key: str):
        """
        Initialize the AnthropicClient.

        Args:
            api_key (str): The API key for authenticating with Anthropic.
        """
        self.client = Anthropic(api_key=api_key)

    def create_message(self, model: str, system: str, messages: List[Dict[str, str]], 
                       functions: List[Dict[str, object]] | None = None, 
                       function_call: str | None = None) -> object:
        """
        Create a message using the Anthropic API.

        Args:
            model (str): The name of the model to use.
            system (str): The system message to set the context.
            messages (List[Dict[str, str]]): The conversation history.
            functions (List[Dict[str, object]], optional): List of available functions.
            function_call (str, optional): The name of the function to call.

        Returns:
            object: The API response object.
        """
        model_data = config.get_model("text_models", "anthropic", model)
        
        # Prepare the messages
        formatted_messages = [{"role": "system", "content": system}] + messages
        
        # Prepare the API call parameters
        params = {
            "model": model,
            "max_tokens": model_data['max_tokens'],
            "messages": formatted_messages,
        }
        
        # Add functions if provided
        if functions:
            params["tools"] = functions
            if function_call:
                params["tool_choice"] = {"type": "function", "function": {"name": function_call}}

        response = self.client.messages.create(**params)

        # Handle tool calls if present in the response
        if hasattr(response, 'content') and any(c.type == 'tool_calls' for c in response.content):
            tool_calls = next(c.tool_calls for c in response.content if c.type == 'tool_calls')
            tool_results = self.execute_tool_calls(tool_calls)
            
            # Make a follow-up API call with tool results
            formatted_messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls
            })
            formatted_messages.append({
                "role": "tool",
                "content": json.dumps(tool_results)
            })
            
            response = self.client.messages.create(**params)

        return response

    def get_output_tokens(self, response: object) -> int:
        """
        Get the number of output tokens from the API response.

        Args:
            response (object): The API response object.

        Returns:
            int: The number of output tokens.
        """
        return response.usage.output_tokens if hasattr(response, 'usage') else 0

    def execute_tool_calls(self, tool_calls: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        Execute tool calls based on the API response.

        Args:
            tool_calls (List[Dict[str, object]]): The tool calls to execute.

        Returns:
            List[Dict[str, object]]: The results of the tool calls.
        """
        # This method should be implemented to execute the tool calls
        # It could involve calling external APIs, databases, or other functions
        # For now, we'll return a placeholder result
        return [{"result": f"Executed {tool_call.function.name}"} for tool_call in tool_calls]

class OpenAIClient(AIClient):
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def create_message(self, model: str, system: str, messages: List[Dict[str, str]], 
                       functions: List[Dict[str, object]] | None = None, 
                       function_call: str | None = None) -> object:
        model_data = config.get_model("text_models", "openai", model)
        
        # Prepare the messages
        formatted_messages = [{"role": "system", "content": system}] + messages
        
        # Prepare the API call parameters
        params = {
            "model": model,
            "messages": formatted_messages,
            "max_tokens": model_data['max_tokens'],
        }
        
        # Add functions if provided
        if functions:
            params["functions"] = functions
            if function_call:
                params["function_call"] = function_call

        response = openai.ChatCompletion.create(**params)

        # Handle function calls if present in the response
        if 'function_call' in response['choices'][0]['message']:
            function_call = response['choices'][0]['message']['function_call']
            function_results = self.execute_tool_calls([function_call])
            
            # Make a follow-up API call with function results
            formatted_messages.append({
                "role": "assistant",
                "content": None,
                "function_call": function_call
            })
            formatted_messages.append({
                "role": "function",
                "name": function_call['name'],
                "content": json.dumps(function_results[0])
            })
            
            response = openai.ChatCompletion.create(**params)

        return response

    def get_output_tokens(self, response: object) -> int:
        return response['usage']['completion_tokens'] if 'usage' in response else 0

    def execute_tool_calls(self, tool_calls: List[Dict[str, object]]) -> List[Dict[str, object]]:
        # This method should be implemented to execute the tool calls
        # It could involve calling external APIs, databases, or other functions
        # For now, we'll return a placeholder result
        return [{"result": f"Executed {tool_call['name']}"} for tool_call in tool_calls]

from typing import List, Dict
from groq import Groq
import json
from config import config

class GroqClient:
    """
    A client for interacting with the Groq API.
    """

    def __init__(self, api_key: str):
        """
        Initialize the GroqClient.

        Args:
            api_key (str): The API key for authenticating with Groq.
        """
        self.client = Groq(api_key=api_key)

    def create_message(self, model: str, system: str, messages: List[Dict[str, str]], 
                       functions: List[Dict[str, object]] | None = None, 
                       function_call: str | None = None) -> object:
        """
        Create a message using the Groq API.

        Args:
            model (str): The name of the model to use.
            system (str): The system message to set the context.
            messages (List[Dict[str, str]]): The conversation history.
            functions (List[Dict[str, object]], optional): List of available functions.
            function_call (str, optional): The name of the function to call.

        Returns:
            object: The API response object.
        """
        model_data = config.get_model("text_models", "groq", model)
        
        # Prepare messages in the correct format
        formatted_messages = [{"role": "system", "content": system}] + messages

        # Prepare API call parameters
        params = {
            "model": model,
            "messages": formatted_messages,
            "max_tokens": model_data['max_tokens'],
        }

        # Add functions if provided
        if functions:
            params["functions"] = functions
            if function_call:
                params["function_call"] = {"name": function_call}

        response = self.client.chat.completions.create(**params)

        # Handle function calls if present in the response
        if hasattr(response.choices[0].message, 'function_call') and response.choices[0].message.function_call:
            function_call = response.choices[0].message.function_call
            tool_results = self.execute_tool_calls([function_call])
            
            # Make a follow-up API call with tool results
            formatted_messages.append({
                "role": "assistant",
                "content": None,
                "function_call": function_call
            })
            formatted_messages.append({
                "role": "function",
                "name": function_call.name,
                "content": json.dumps(tool_results[0])
            })
            
            response = self.client.chat.completions.create(**params)

        return response

    def get_output_tokens(self, response: object) -> int:
        """
        Get the number of output tokens from the API response.

        Args:
            response (object): The API response object.

        Returns:
            int: The number of output tokens.
        """
        return response.usage.completion_tokens if hasattr(response, 'usage') else 0

    def execute_tool_calls(self, tool_calls: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        Execute tool calls based on the API response.

        Args:
            tool_calls (List[Dict[str, object]]): The tool calls to execute.

        Returns:
            List[Dict[str, object]]: The results of the tool calls.
        """
        # This method should be implemented to execute the tool calls
        # It could involve calling external APIs, databases, or other functions
        # For now, we'll return a placeholder result
        return [{"result": f"Executed {tool_call['name']}"} for tool_call in tool_calls]

class AIClientFactory:
    _clients = {}

    @staticmethod
    def get_client(provider: str) -> AIClient:
        if provider not in AIClientFactory._clients:
            api_key = config.valid_apis.get(provider)
            if not api_key:
                raise ValueError(f"No API key found for provider: {provider}")
            
            if provider == "anthropic":
                AIClientFactory._clients[provider] = AnthropicClient(api_key)
            elif provider == "openai":
                AIClientFactory._clients[provider] = OpenAIClient(api_key)
            elif provider == "groq":
                AIClientFactory._clients[provider] = GroqClient(api_key)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        
        return AIClientFactory._clients[provider]

    @staticmethod
    def get_model(model_type: str, provider: str, model_name: str) -> Dict[str, object]:
        return config.get_model(model_type, provider, model_name)