import tiktoken
from typing import Dict

# Initialize the tokenizer
try:
    tokenizer = tiktoken.get_encoding("cl100k_base")
except KeyError:
    print("Warning: cl100k_base encoding not found. Falling back to p50k_base.")
    tokenizer = tiktoken.get_encoding("p50k_base")

# Global variable to store token usage
token_usage: Dict[str, object] = {
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

def update_token_usage(input_tokens: int, output_tokens: int, total_tokens: int, system_tokens: int, history_tokens: int, provider: str) -> None:
    """
    Update the global token usage statistics with the latest interaction's token counts.

    Args:
        input_tokens (int): Number of tokens in the user's input.
        output_tokens (int): Number of tokens in the AI's response.
        total_tokens (int): Total number of tokens in the interaction.
        system_tokens (int): Number of tokens in the system prompt.
        history_tokens (int): Number of tokens in the conversation history.
        provider (str): The AI provider used for this interaction.
    """
    global token_usage
    token_usage["total_tokens"] += total_tokens
    token_usage["conversation_tokens"].append({
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "system_tokens": system_tokens,
        "history_tokens": history_tokens,
        "total_tokens": total_tokens,
        "provider": provider
    })

def get_token_usage() -> Dict[str, object]:
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
            "total_tokens": 0,
            "provider": "N/A"
        }
        average_tokens = 0

    return {
        "total_tokens": total_tokens,
        "average_tokens_per_message": average_tokens,
        "last_message": last_message,
        "conversation_tokens": conversation_tokens
    }

def display_token_usage(usage: Dict[str, object], is_summary: bool = False) -> str:
    """
    Generate a display string for token usage statistics.

    Args:
        usage (Dict[str, object]): Token usage statistics.
        is_summary (bool): Whether to display a summary or detailed view.

    Returns:
        str: Formatted string displaying token usage statistics.
    """
    display = ""
    if is_summary:
        display += "Token Usage Summary:\n"
        display += f"Total Conversations: {len(usage.get('conversation_tokens', []))}\n"
        display += f"Total Tokens Used: {usage.get('total_tokens', 0)}\n"
        
        # Add provider-specific summary
        provider_summary = {}
        for conv in usage.get('conversation_tokens', []):
            provider = conv['provider']
            if provider not in provider_summary:
                provider_summary[provider] = 0
            provider_summary[provider] += conv['total_tokens']
        
        display += "Tokens Used by Provider:\n"
        for provider, tokens in provider_summary.items():
            display += f"  {provider}: {tokens}\n"
    else:
        display += "Conversation Token Usage:\n"
        display += f"Input Tokens: {usage.get('input_tokens', 0)}\n"
        display += f"Output Tokens: {usage.get('output_tokens', 0)}\n"
        display += f"Total Conversation Tokens: {usage.get('total_tokens', 0)}\n"
        display += f"Provider: {usage.get('provider', 'N/A')}\n"
        
        if 'system_tokens' in usage:
            display += f"System Prompt Tokens: {usage['system_tokens']}\n"
        
        if 'history_tokens' in usage:
            display += f"Conversation History Tokens: {usage['history_tokens']}\n"
    
    return display

def reset_token_usage() -> None:
    """Reset the token usage statistics."""
    global token_usage
    token_usage = {
        "total_tokens": 0,
        "conversation_tokens": []
    }