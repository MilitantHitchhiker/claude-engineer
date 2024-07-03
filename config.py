# config.py

import os

# Constants
MAX_CONTINUATION_ITERATIONS = 25
CONTINUATION_EXIT_PHRASE = "AUTOMODE_COMPLETE"

# Color constants
from colorama import Fore

USER_COLOR = Fore.WHITE
CLAUDE_COLOR = Fore.BLUE
TOOL_COLOR = Fore.YELLOW
RESULT_COLOR = Fore.GREEN

# API configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

# Validate API keys
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY environment variable is not set")