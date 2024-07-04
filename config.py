import os
import json
from anthropic import Anthropic
import openai
from groq import Groq

def load_model_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Model data file not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON format in model data file: {file_path}")
        return {}

def validate_api_key(api_name, api_key):
    if not api_key:
        print(f"{api_name} API key is empty or not provided.")
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
        # Add validation for other API providers as needed
        return True
    except Exception as e:
        print(f"Error validating {api_name} API key: {str(e)}")
        return False

# Load API keys from system environment variables only
API_KEYS = {
    "anthropic": os.environ.get('ANTHROPIC_API_KEY'),
    "openai": os.environ.get('OPENAI_API_KEY'),
    "groq": os.environ.get('GROQ_API_KEY'),
    # Add other API keys as needed
}

# Validate API keys
for api_name, api_key in API_KEYS.items():
    if not validate_api_key(api_name, api_key):
        print(f"Warning: Invalid {api_name.upper()}_API_KEY. This provider will not be available.")
        API_KEYS[api_name] = None

# Load model data from external JSON file
MODEL_DATA_FILE = os.environ.get('MODEL_DATA_FILE', 'models.json')
MODEL_DATA = load_model_data(MODEL_DATA_FILE)

# Automode Configuration
MAX_CONTINUATION_ITERATIONS = int(os.environ.get('MAX_CONTINUATION_ITERATIONS', '10'))
MAX_CONTINUATION_TOKENS = int(os.environ.get('MAX_CONTINUATION_TOKENS', '50000'))
CONTINUATION_EXIT_PHRASE = os.environ.get('CONTINUATION_EXIT_PHRASE', 'AUTOMODE_COMPLETE')

# Color Configuration  
USER_COLOR = os.environ.get('USER_COLOR', '\033[94m')  # Blue
CLAUDE_COLOR = os.environ.get('CLAUDE_COLOR', '\033[92m')  # Green
TOOL_COLOR = os.environ.get('TOOL_COLOR', '\033[93m')  # Yellow
RESULT_COLOR = os.environ.get('RESULT_COLOR', '\033[95m')  # Magenta

class AIModelSelector:
    @staticmethod
    def get_model(model_type, provider, model_name):
        try:
            return MODEL_DATA[model_type][provider][model_name]
        except KeyError:
            raise ValueError(f"Model not found: {model_type} - {provider} - {model_name}")

    @staticmethod
    def list_models(model_type=None, provider=None):
        if model_type and provider:
            return MODEL_DATA.get(model_type, {}).get(provider, {})
        elif model_type:
            return MODEL_DATA.get(model_type, {})
        else:
            return MODEL_DATA

# Example usage
# text_model = AIModelSelector.get_model("text_models", "anthropic", "claude-3-opus-20240229")
# vision_model = AIModelSelector.get_model("vision_models", "openai", "gpt-4-vision-preview")
# all_image_gen_models = AIModelSelector.list_models("image_generation_models")