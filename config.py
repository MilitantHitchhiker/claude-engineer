"""
Configuration module for Claude Engineer application.
Loads configuration from .env file and falls back to system environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# Model Configuration
MODEL_NAME = os.getenv('MODEL_NAME', 'claude-3.5-sonnet-20240620')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '4000'))

# Automode Configuration
MAX_CONTINUATION_ITERATIONS = int(os.getenv('MAX_CONTINUATION_ITERATIONS', '10'))
CONTINUATION_EXIT_PHRASE = os.getenv('CONTINUATION_EXIT_PHRASE', 'AUTOMODE_COMPLETE')

# Color Configuration
USER_COLOR = os.getenv('USER_COLOR', '\033[94m')  # Blue
CLAUDE_COLOR = os.getenv('CLAUDE_COLOR', '\033[92m')  # Green
TOOL_COLOR = os.getenv('TOOL_COLOR', '\033[93m')  # Yellow
RESULT_COLOR = os.getenv('RESULT_COLOR', '\033[95m')  # Magenta

# Validate required configuration
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set. Please set it in your .env file or system environment.")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not set. Please set it in your .env file or system environment.")

# Optional: Add any other configuration variables your application needs

# Example of how to add a new configuration variable:
# DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'