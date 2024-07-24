import os
from dotenv import load_dotenv
import json
from anthropic import Anthropic, APIStatusError, APIError
import openai
from openai import OpenAIError
from groq import Groq
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        logger.debug("Initializing Config...")
        load_dotenv()  # Load environment variables from .env file
        self.api_keys = self.load_api_keys()
        logger.debug(f"Loaded API keys: {self.masked_api_keys()}")
        self.model_data = self.load_model_data()
        logger.debug(f"Loaded model data: {self.model_data}")
        self.valid_apis = self.validate_api_keys()
        logger.debug(f"Validated API keys: {self.masked_valid_apis()}")

    def load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables."""
        api_keys = {
            "anthropic": os.environ.get('ANTHROPIC_API_KEY'),
            "openai": os.environ.get('OPENAI_API_KEY'),
            "groq": os.environ.get('GROQ_API_KEY'),
            "tavily": os.environ.get('TAVILY_API_KEY'),
        }
        return api_keys

    def validate_api_keys(self) -> Dict[str, str]:
        """Validate API keys by attempting to use them."""
        valid_apis = {}
        for api_name, api_key in self.api_keys.items():
            if self.validate_api_key(api_name, api_key):
                valid_apis[api_name] = api_key
        return valid_apis

    def validate_api_key(self, api_name: str, api_key: str) -> bool:
        """Validate a single API key by attempting to use it."""
        if not api_key:
            logger.info(f"API key for {api_name} is not provided.")
            return False

        try:
            if api_name == "anthropic":
                client = Anthropic(api_key=api_key)
                model = self.get_available_model("text_models", "anthropic")
                client.messages.create(
                    model=model,
                    max_tokens=1,
                    messages=[{"role": "user", "content": "Hello"}]
                )
            elif api_name == "openai":
                client = openai.OpenAI(api_key=api_key)
                model = self.get_available_model("text_models", "openai")
                client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=1
                )
            elif api_name == "groq":
                client = Groq(api_key=api_key)
                model = self.get_available_model("text_models", "groq")
                client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=1
                )
            elif api_name == "tavily":
                return True  # Assuming valid if provided
            else:
                logger.warning(f"Unknown API: {api_name}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Error validating API key for {api_name}: {type(e).__name__} - {str(e)}")
            return False

    def load_model_data(self, file_path: str = 'models.json') -> Dict[str, Any]:
        """Load model data from a JSON file."""
        try:
            with open(file_path, 'r') as file:
                model_data = json.load(file)
                logger.debug(f"Model data loaded from {file_path}: {model_data}")
                return model_data
        except FileNotFoundError:
            logger.error(f"Model data file not found: {file_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in model data file: {file_path}")
            return {}

    def get_available_model(self, model_type: str, provider: str) -> str:
        """Get an available model for the given type and provider."""
        if model_type in self.model_data and provider in self.model_data[model_type]:
            available_models = self.model_data[model_type][provider]
            if available_models:
                return next(iter(available_models))  # Return the first available model
        return None

    def get_model(self, model_type: str, provider: str, model_name: str) -> Dict[str, Any]:
        """Get model data for a specific model."""
        try:
            return self.model_data[model_type][provider][model_name]
        except KeyError:
            raise ValueError(f"Model not found: {model_type} - {provider} - {model_name}")

    def list_models(self, model_type: str = None, provider: str = None) -> Dict[str, Any]:
        """List available models, optionally filtered by type and provider."""
        if model_type and provider:
            return self.model_data.get(model_type, {}).get(provider, {})
        elif model_type:
            return self.model_data.get(model_type, {})
        else:
            return self.model_data

    def masked_api_keys(self) -> Dict[str, str]:
        """Return a masked version of the API keys for logging purposes."""
        return {k: (v[:5] + '*****') if v else None for k, v in self.api_keys.items()}

    def masked_valid_apis(self) -> Dict[str, str]:
        """Return a masked version of the valid API keys for logging purposes."""
        return {k: (v[:5] + '*****') if v else None for k, v in self.valid_apis.items()}

# Initialize configuration
config = Config()

class AIModelSelector:
    @staticmethod
    def get_available_model(model_type: str, provider: str) -> str:
        """Get an available model for the given type and provider."""
        return config.get_available_model(model_type, provider)

    @staticmethod
    def get_model(model_type: str, provider: str, model_name: str) -> Dict[str, Any]:
        """Get model data for a specific model."""
        return config.get_model(model_type, provider, model_name)

    @staticmethod
    def list_models(model_type: str = None, provider: str = None) -> Dict[str, Any]:
        """List available models, optionally filtered by type and provider."""
        return config.list_models(model_type, provider)

# Constants from the config file
MAX_CONTINUATION_ITERATIONS = int(os.environ.get('MAX_CONTINUATION_ITERATIONS', '10'))
MAX_CONTINUATION_TOKENS = int(os.environ.get('MAX_CONTINUATION_TOKENS', '50000'))
CONTINUATION_EXIT_PHRASE = os.environ.get('CONTINUATION_EXIT_PHRASE', 'AUTOMODE_COMPLETE')

# Color Configuration
USER_COLOR = os.environ.get('USER_COLOR', '\033[94m')  # Blue
CLAUDE_COLOR = os.environ.get('CLAUDE_COLOR', '\033[92m')  # Green
TOOL_COLOR = os.environ.get('TOOL_COLOR', '\033[93m')  # Yellow
RESULT_COLOR = os.environ.get('RESULT_COLOR', '\033[95m')  # Magenta