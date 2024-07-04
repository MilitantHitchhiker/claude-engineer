"""
This module handles token tracking and usage statistics for the Claude chat application.
It provides functions for counting tokens, updating usage statistics, and generating token usage information.
"""

import tiktoken
from typing import Dict, Any

# Initialize the tokenizer
try:
    tokenizer = tiktoken.get_encoding("cl100k_base")
except KeyError:
    print("Warning: cl100k_base encoding not found. Falling back to p50k_base.")
    tokenizer = tiktoken.get_encoding("p50k_base")

# Global variable to store token usage
token_usage: Dict[str, Any] = {
    "total_tokens": 0,
    "conversation_tokens": []
}

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in the given text.

    Args:
        text (str): The input text to tokenize.

    Returns:
        int: The number of tokens in the text.
    """
    return len(tokenizer.encode(text))

def update_token_usage(input_tokens: int, output_tokens: int, total_tokens: int, system_tokens: int, history_tokens: int) -> None:
    """
    Update the global token usage statistics with the latest interaction's token counts.

    Args:
        input_tokens (int): Number of tokens in the user's input.
        output_tokens (int): Number of tokens in the AI's response.
        total_tokens (int): Total number of tokens in the interaction.
        system_tokens (int): Number of tokens in the system prompt.
        history_tokens (int): Number of tokens in the conversation history.
    """
    global token_usage
    token_usage["total_tokens"] += total_tokens
    token_usage["conversation_tokens"].append({
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "system_tokens": system_tokens,
        "history_tokens": history_tokens,
        "total_tokens": total_tokens
    })

def get_token_usage() -> Dict[str, Any]:
    """
    Retrieve the current token usage statistics.

    Returns:
        dict: A dictionary containing total tokens used, average tokens per message,
              last message token usage, and a list of all conversation token usages.
    """
    global token_usage
    total_tokens = token_usage["total_tokens"]
    conversation_tokens = token_usage["conversation_tokens"]
    
    if conversation_tokens:
        last_message = conversation_tokens[-1]
        average_tokens = total_tokens / len(conversation_tokens)
    else:
        last_message = {
            "input_tokens": 0,
            "output_tokens": 0,
            "system_tokens": 0,
            "history_tokens": 0,
            "total_tokens": 0
        }
        average_tokens = 0

    return {
        "total_tokens": total_tokens,
        "average_tokens_per_message": average_tokens,
        "last_message": last_message,
        "conversation_tokens": conversation_tokens
    }

def display_token_usage(usage, is_summary=False):
    display = ""
    if is_summary:
        display += "Token Usage Summary:\n"
        display += f"Total Conversations: {len(usage.get('conversation_tokens', []))}\n"
        display += f"Total Tokens Used: {usage.get('total_tokens', 0)}\n"
    else:
        display += "Conversation Token Usage:\n"
        display += f"Input Tokens: {usage.get('input_tokens', 0)}\n"
        display += f"Output Tokens: {usage.get('output_tokens', 0)}\n"
        display += f"Total Conversation Tokens: {usage.get('total_tokens', 0)}\n"
        
        if 'system_prompt_tokens' in usage:
            display += f"System Prompt Tokens: {usage['system_prompt_tokens']}\n"
        
        if 'conversation_history_tokens' in usage:
            display += f"Conversation History Tokens: {usage['conversation_history_tokens']}\n"
        
        if 'last_message' in usage:
            last_message = usage['last_message']
            display += f"\nLast Message:\n{last_message}\n"
    
    return display