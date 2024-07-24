from ai_client_base import AIClient
from config import Config
from anthropic import Anthropic
import openai
from groq import Groq
from typing import List, Dict, Any
import json
from tools import execute_tool_calls as execute_tool

# Initialize Config
config = Config()

class AnthropicClient(AIClient):
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
                       functions: List[Dict[str, object]] = None, 
                       function_call: str = None) -> object:
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
        # Get model data
        model_data = config.get_model("text_models", "anthropic", model)
        
        # Prepare the API call parameters
        params = {
            "model": model,
            "system": system,  # System message as a top-level parameter
            "messages": messages,
            "max_tokens": model_data['max_tokens'],
            "temperature": model_data['temperature'],
        }
        
        # Add functions if provided
        if functions:
            tools = []
            for function in functions:
                tool = {
                    "name": function.get("name"),
                    "description": function.get("description"),
                    "input_schema": {"type": "object"}
                }
                tools.append(tool)
            params["tools"] = tools
            if function_call:
                params["tool_choice"] = function_call if function_call != "auto" else {"type": "tool", "name": functions[0]["name"]}

        # Make the initial API call
        response = self.client.messages.create(**params)

        # Extract tool calls from the response
        tool_calls = []
        for content_block in response.content:
            if content_block.type == "tool_calls":
                tool_calls.extend(content_block.tool_calls)
        
        # Execute tool calls if present
        if tool_calls:
            tool_results = self.execute_tool_calls(tool_calls)
            messages.extend(tool_results)
            # Make a follow-up API call with tool results
            response = self.client.messages.create(
                model=model,
                system=system,
                messages=messages,
                max_tokens=model_data['max_tokens'],
                temperature=model_data['temperature'],
                tools=tools,
                tool_choice={"type": "tool", "name": tool_calls[0]["name"]} if tool_calls else None
            )

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
    """
    A client for interacting with the OpenAI API.
    """

    def __init__(self, api_key: str):
        """
        Initialize the OpenAIClient.

        Args:
            api_key (str): The API key for authenticating with OpenAI.
        """
        self.client = openai.OpenAI(api_key=api_key)

    def create_message(self, model: str, system: str, messages: List[Dict[str, str]], 
                       functions: List[Dict[str, object]] = None, 
                       function_call: str = None) -> object:
        """
        Create a message using the OpenAI API.

        Args:
            model (str): The name of the model to use.
            system (str): The system message to set the context.
            messages (List[Dict[str, str]]): The conversation history.
            functions (List[Dict[str, object]], optional): List of available functions.
            function_call (str, optional): The name of the function to call.

        Returns:
            object: The API response object.
        """
        # Get model data
        model_data = config.get_model("text_models", "openai", model)
        
        # Prepare the API call parameters
        params = {
            "model": model,
            "system": system,  # System message as a top-level parameter
            "messages": messages,
            "max_tokens": model_data['max_tokens'],
            "temperature": model_data['temperature'],
        }
        
        # Add functions if provided
        if functions:
            tools = []
            for function in functions:
                tool = {
                    "name": function.get("name"),
                    "description": function.get("description"),
                    "input_schema": {"type": "object"}
                }
                tools.append(tool)
            params["functions"] = tools
            if function_call:
                params["function_call"] = function_call if function_call != "auto" else {"type": "tool", "name": functions[0]["name"]}

        # Make the initial API call
        response = self.client.chat.completions.create(**params)

        # Check for function calls in the response
        function_call = response.choices[0].message.function_call
        if function_call:
            function_results = self.execute_tool_calls([function_call])
            messages.extend(function_results)
            # Make a follow-up API call with function results
            response = self.client.chat.completions.create(
                model=model,
                system=system,
                messages=messages,
                max_tokens=model_data['max_tokens'],
                temperature=model_data['temperature'],
                functions=tools,
                function_call={"type": "tool", "name": function_call.name} if function_call else None
            )

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
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.name
            tool_arguments = json.loads(tool_call.arguments)
            result = execute_tool(tool_name, tool_arguments)
            results.append({
                "role": "function",
                "name": tool_name,
                "content": result
            })
        return results

class GroqClient(AIClient):
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
                       functions: List[Dict[str, object]] = None, 
                       function_call: str = None) -> object:
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
        # Get model data
        model_data = config.get_model("text_models", "groq", model)
        
        # Prepare the API call parameters
        params = {
            "model": model,
            "system": system,  # System message as a top-level parameter
            "messages": messages,
            "max_tokens": model_data['max_tokens'],
            "temperature": model_data['temperature'],
        }

        # Add functions if provided
        if functions:
            tools = []
            for function in functions:
                tool = {
                    "name": function.get("name"),
                    "description": function.get("description"),
                    "input_schema": {"type": "object"}
                }
                tools.append(tool)
            params["functions"] = tools
            if function_call:
                params["function_call"] = function_call if function_call != "auto" else {"type": "tool", "name": functions[0]["name"]}

        # Make the initial API call
        response = self.client.chat.completions.create(**params)

        # Check for function calls in the response
        function_call = response.choices[0].message.function_call
        if function_call:
            function_results = self.execute_tool_calls([function_call])
            messages.extend(function_results)
            # Make a follow-up API call with function results
            response = self.client.chat.completions.create(
                model=model,
                system=system,
                messages=messages,
                max_tokens=model_data['max_tokens'],
                temperature=model_data['temperature'],
                functions=tools,
                function_call={"type": "tool", "name": function_call.name} if function_call else None
            )

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
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.name
            tool_arguments = json.loads(tool_call.arguments)
            result = execute_tool(tool_name, tool_arguments)
            results.append({
                "role": "function",
                "name": tool_name,
                "content": result
            })
        return results

class AIClientFactory:
    """
    A factory class for creating AI clients based on the provider.
    """
    _clients = {}

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
    def get_model(model_type: str, provider: str, model_name: str) -> Dict[str, object]:
        """
        Get the model data for a specific model.

        Args:
            model_type (str): The type of the model (e.g., "text_models").
            provider (str): The name of the AI provider.
            model_name (str): The name of the model.

        Returns:
            Dict[str, object]: The model data.
        """
        return config.get_model(model_type, provider, model_name)
