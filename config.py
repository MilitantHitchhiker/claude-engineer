import os
import json
from anthropic import Anthropic
import openai
from groq import Groq
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.api_keys = self.load_api_keys()
        self.valid_apis = self.validate_api_keys()
        self.model_data = self.load_model_data()

    def load_api_keys(self):
        return {
            "anthropic": os.environ.get('ANTHROPIC_API_KEY'),
            "openai": os.environ.get('OPENAI_API_KEY'),
            "groq": os.environ.get('GROQ_API_KEY'),
            "tavily": os.environ.get('TAVILY_API_KEY'),
        }

    def validate_api_keys(self):
        valid_apis = {}
        for api_name, api_key in self.api_keys.items():
            if self.validate_api_key(api_name, api_key):
                valid_apis[api_name] = api_key
        return valid_apis

    def validate_api_key(self, api_name: str, api_key: str) -> bool:
        if not api_key:
            logger.info(f"API key for {api_name} is not provided.")
            return False

        try:
            if api_name == "anthropic":
                client = Anthropic(api_key=api_key)
                client.completions.create(prompt="Test", model="claude-3-sonnet-20240229", max_tokens_to_sample=1)
            elif api_name == "openai":
                openai.api_key = api_key
                openai.Model.list()
            elif api_name == "groq":
                client = Groq(api_key=api_key)
                client.models.list()
            elif api_name == "tavily":
                return True  # Assuming valid if provided
            else:
                logger.warning(f"Unknown API: {api_name}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Error validating API key for {api_name}: {type(e).__name__}")
            return False

    def load_model_data(self, file_path: str = 'models.json'):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logger.error(f"Model data file not found: {file_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in model data file: {file_path}")
            return {}

    def get_available_model(self, model_type: str, provider: str):
        if model_type in self.model_data and provider in self.model_data[model_type]:
            available_models = self.model_data[model_type][provider]
            if available_models:
                return next(iter(available_models))  # Return the first available model
        return None

    def get_model(self, model_type: str, provider: str, model_name: str):
        try:
            return self.model_data[model_type][provider][model_name]
        except KeyError:
            raise ValueError(f"Model not found: {model_type} - {provider} - {model_name}")

    def list_models(self, model_type: str = None, provider: str = None):
        if model_type and provider:
            return self.model_data.get(model_type, {}).get(provider, {})
        elif model_type:
            return self.model_data.get(model_type, {})
        else:
            return self.model_data

# Initialize configuration
config = Config()

class AIModelSelector:
    @staticmethod
    def get_available_model(model_type: str, provider: str):
        return config.get_available_model(model_type, provider)

    @staticmethod
    def get_model(model_type: str, provider: str, model_name: str):
        return config.get_model(model_type, provider, model_name)

    @staticmethod
    def list_models(model_type: str = None, provider: str = None):
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
