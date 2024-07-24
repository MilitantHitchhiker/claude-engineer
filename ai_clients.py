"""
ai_clients.py

This module contains client classes for interacting with various AI providers' APIs.
It includes implementations for Anthropic, OpenAI, and Groq.

Each client class inherits from the AIClient base class and implements provider-specific
logic for creating messages, executing tool calls, and handling responses.
"""

import json
import logging
from typing import List, Dict, Any, Union

from anthropic import Anthropic
import openai
from groq import Groq

from ai_client_base import AIClient
from config import Config
from tools import execute_tool
# Initialize Config
config = Config()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnthropicClient(AIClient):
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    def create_message(self, model: str, system: str, messages: List[Dict[str, str]]) -> Any:
        try:
            # Get model data
            model_data = config.get_model("text_models", "anthropic", model)
            
            # Prepare the API call parameters
            params = {
                "model": model,
                "max_tokens": model_data['max_tokens'],
                "temperature": model_data['temperature'],
                "system": system,
                "messages": [msg for msg in messages if msg['role'] != 'system']
            }

            # Make the API call
            logger.info(f"Making Anthropic API call with params: {params}")
            response = self.client.messages.create(**params)

            return response

        except Exception as e:
            logger.error(f"Error in Anthropic API call: {str(e)}")
            raise Exception(f"Error in Anthropic API call: {str(e)}")

    def get_output_tokens(self, response: Any) -> int:
        return response.usage.output_tokens if hasattr(response, 'usage') else 0

    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_arguments = json.loads(tool_call.function.arguments)
            result = execute_tool(tool_name, tool_arguments)
            results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": result
            })
        return results

class OpenAIClient(AIClient):
    """Client for interacting with the OpenAI API."""

    def __init__(self, api_key: str):
        """
        Initialize the OpenAIClient.

        Args:
            api_key (str): The API key for authenticating with OpenAI.
        """
        self.client = openai.OpenAI(api_key=api_key)

    def create_message(self, model: str, system: str, messages: List[Dict[str, str]], 
                       functions: List[Dict[str, Any]] = None, 
                       function_call: str = None) -> Dict[str, Any]:
        """
        Create a message using the OpenAI API.

        Args:
            model (str): The name of the model to use.
            system (str): The system message to set the context.
            messages (List[Dict[str, str]]): The conversation history.
            functions (List[Dict[str, Any]], optional): List of available functions.
            function_call (str, optional): The name of the function to call.

        Returns:
            Dict[str, Any]: The API response as a dictionary.

        Raises:
            Exception: If there's an error in the API call.
        """
        try:
            # Get model data
            model_data = config.get_model("text_models", "openai", model)
            
            # Prepare the API call parameters
            params = {
                "model": model,
                "messages": [{"role": "system", "content": system}, *messages],
                "max_tokens": model_data['max_tokens'],
                "temperature": model_data['temperature'],
            }
            
            # Add functions if provided
            if functions:
                params["functions"] = functions
                if function_call:
                    params["function_call"] = function_call if function_call != "auto" else "auto"

            # Make the API call
            logger.info(f"Making OpenAI API call with params: {params}")
            response = self.client.chat.completions.create(**params)

            return response.model_dump()

        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise Exception(f"Error in OpenAI API call: {str(e)}")

    def get_output_tokens(self, response: Dict[str, Any]) -> int:
        """
        Get the number of output tokens from the API response.

        Args:
            response (Dict[str, Any]): The API response dictionary.

        Returns:
            int: The number of output tokens.
        """
        return response.get('usage', {}).get('completion_tokens', 0)

    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute tool calls based on the API response.

        Args:
            tool_calls (List[Dict[str, Any]]): The tool calls to execute.

        Returns:
            List[Dict[str, Any]]: The results of the tool calls.
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_arguments = json.loads(tool_call["function"]["arguments"])
            result = self.execute_tool(tool_name, tool_arguments)
            results.append({
                "role": "function",
                "name": tool_name,
                "content": result
            })
        return results

class GroqClient(AIClient):
    """Client for interacting with the Groq API."""

    def __init__(self, api_key: str):
        """
        Initialize the GroqClient.

        Args:
            api_key (str): The API key for authenticating with Groq.
        """
        self.client = Groq(api_key=api_key)

    def create_message(self, model: str, system: str, messages: List[Dict[str, str]], 
                       functions: List[Dict[str, Any]] = None, 
                       function_call: str = None) -> Dict[str, Any]:
        """
        Create a message using the Groq API.

        Args:
            model (str): The name of the model to use.
            system (str): The system message to set the context.
            messages (List[Dict[str, str]]): The conversation history.
            functions (List[Dict[str, Any]], optional): List of available functions.
            function_call (str, optional): The name of the function to call.

        Returns:
            Dict[str, Any]: The API response as a dictionary.

        Raises:
            Exception: If there's an error in the API call.
        """
        try:
            # Get model data
            model_data = config.get_model("text_models", "groq", model)
            
            # Prepare the API call parameters
            params = {
                "model": model,
                "messages": [{"role": "system", "content": system}, *messages],
                "max_tokens": model_data['max_tokens'],
                "temperature": model_data['temperature'],
            }
            
            # Add functions if provided
            if functions:
                params["functions"] = functions
                if function_call:
                    params["function_call"] = function_call if function_call != "auto" else "auto"

            # Make the API call
            logger.info(f"Making Groq API call with params: {params}")
            response = self.client.chat.completions.create(**params)

            return response.model_dump()

        except Exception as e:
            logger.error(f"Error in Groq API call: {str(e)}")
            raise Exception(f"Error in Groq API call: {str(e)}")

    def get_output_tokens(self, response: Dict[str, Any]) -> int:
        """
        Get the number of output tokens from the API response.

        Args:
            response (Dict[str, Any]): The API response dictionary.

        Returns:
            int: The number of output tokens.
        """
        return response.get('usage', {}).get('completion_tokens', 0)

    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute tool calls based on the API response.

        Args:
            tool_calls (List[Dict[str, Any]]): The tool calls to execute.

        Returns:
            List[Dict[str, Any]]: The results of the tool calls.
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_arguments = json.loads(tool_call["function"]["arguments"])
            result = self.execute_tool(tool_name, tool_arguments)
            results.append({
                "role": "function",
                "name": tool_name,
                "content": result
            })
        return results

class AIClientFactory:
    """Factory class for creating AI clients based on the provider."""

    _clients: Dict[str, AIClient] = {}

    @staticmethod
    def get_client(provider: str) -> AIClient:
        """
        Get or create an AI client for the specified provider.

        Args:
            provider (str): The name of the AI provider.

        Returns:
            AIClient: An instance of the appropriate AI client.

        Raises:
            ValueError: If no API key is found for the provider or if the provider is unsupported.
        """
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
    def get_model(model_type: str, provider: str, model_name: str) -> Dict[str, Any]:
        """
        Get the model data for a specific model.

        Args:
            model_type (str): The type of the model (e.g., "text_models").
            provider (str): The name of the AI provider.
            model_name (str): The name of the model.

        Returns:
            Dict[str, Any]: The model data.
        """
        return config.get_model(model_type, provider, model_name)