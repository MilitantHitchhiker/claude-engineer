"""
Claude-3.5-Sonnet Engineer Chat with Image Support

This script implements an interactive chat interface with the Claude-3.5-Sonnet AI model,
providing capabilities for software development assistance, image analysis, and autonomous mode operation.

Key features:
- Interactive chat with Claude-3.5-Sonnet
- File and folder operations
- Image processing and analysis
- Web search functionality
- Token usage tracking
- Autonomous mode for extended operations

Usage:
Run this script to start the chat interface. Follow the on-screen instructions for various commands and modes.

Note: Ensure all required modules are installed and API keys are properly set in environment variables before running.
"""

import os
from datetime import datetime
from colorama import init, Style
from typing import List, Dict, Any, Tuple
from config import Config, AIModelSelector, MAX_CONTINUATION_ITERATIONS, MAX_CONTINUATION_TOKENS, CONTINUATION_EXIT_PHRASE, USER_COLOR, CLAUDE_COLOR, TOOL_COLOR, RESULT_COLOR
from ai_clients import AIClientFactory
from token_tracking import count_tokens, update_token_usage, get_token_usage, display_token_usage
from file_operations import read_file, write_to_file, list_files, create_folder, create_file
from image_processing import encode_image_to_base64
from tools import tools, execute_tool
from tavily import TavilyClient

# Initialize colorama
init(autoreset=True)

# Initialise configuration
config = Config()

# Global variables
automode = False
conversation_history = []
default_model = None
clients = {}
tavily_client = None

# System prompt
system_prompt: str = """
You are Claude, an AI assistant powered by Anthropic's Claude-3.5-Sonnet model. You are an exceptional software developer with vast knowledge across multiple programming languages, frameworks, and best practices. Your capabilities include:

1. Creating project structures, including folders and files
2. Writing clean, efficient, and well-documented code
3. Debugging complex issues and providing detailed explanations
4. Offering architectural insights and design patterns
5. Staying up-to-date with the latest technologies and industry trends
6. Reading and analyzing existing files in the project directory
7. Listing files in the root directory of the project
8. Performing web searches to get up-to-date information or additional context
9. When you use search make sure you use the best query to get the most accurate and up-to-date information
10. IMPORTANT!! When editing files, always provide the full content of the file, even if you're only changing a small part. The system will automatically generate and apply the appropriate diff.
11. Analyzing images provided by the user
When an image is provided, carefully analyze its contents and incorporate your observations into your responses.

When asked to create a project:
- Always start by creating a root folder for the project.
- Then, create the necessary subdirectories and files within that root folder.
- Organize the project structure logically and follow best practices for the specific type of project being created.
- Use the provided tools to create folders and files as needed.

When asked to make edits or improvements:
- Use the read_file tool to examine the contents of existing files.
- Analyze the code and suggest improvements or make necessary edits.
- Use the write_to_file tool to implement changes, providing the full updated file content.

Be sure to consider the type of project (e.g., Python, JavaScript, web application) when determining the appropriate structure and files to include.

You can now read files, list the contents of the root folder where this script is being run, and perform web searches. Use these capabilities when:
- The user asks for edits or improvements to existing files
- You need to understand the current state of the project
- You believe reading a file or listing directory contents will be beneficial to accomplish the user's goal
- You need up-to-date information or additional context to answer a question accurately

When you need current information or feel that a search could provide a better answer, use the tavily_search tool. This tool performs a web search and returns a concise answer along with relevant sources.

Always strive to provide the most accurate, helpful, and detailed responses possible. If you're unsure about something, admit it and consider using the search tool to find the most current information.

{automode_status}

When in automode:
1. Set clear, achievable goals for yourself based on the user's request
2. Work through these goals one by one, using the available tools as needed
3. REMEMBER!! You can Read files, write code, LIST the files, and even SEARCH and make edits, use these tools as necessary to accomplish each goal
4. ALWAYS READ A FILE BEFORE EDITING IT IF YOU ARE MISSING CONTENT. Provide regular updates on your progress
5. IMPORTANT RULE!! When you know your goals are completed, DO NOT CONTINUE IN POINTLESS BACK AND FORTH CONVERSATIONS with yourself, if you think we achieved the results established to the original request say "AUTOMODE_COMPLETE" in your response to exit the loop!
6. ULTRA IMPORTANT! You have access to this {iteration_info} amount of iterations you have left to complete the request, you can use this information to make decisions and to provide updates on your progress knowing the amount of responses you have left to complete the request.
Answer the user's request using relevant tools (if they are available). Before calling a tool, do some analysis within <thinking></thinking> tags. First, think about which of the provided tools is the relevant tool to answer the user's request. Second, go through each of the required parameters of the relevant tool and determine if the user has directly provided or given enough information to infer a value. When deciding if the parameter can be inferred, carefully consider all the context to see if it supports a specific value. If all of the required parameters are present or can be reasonably inferred, close the thinking tag and proceed with the tool call. BUT, if one of the values for a required parameter is missing, DO NOT invoke the function (not even with fillers for the missing params) and instead, ask the user to provide the missing parameters. DO NOT ask for more information on optional parameters if it is not provided.
"""

def handle_error(error_message: str, error: Exception = None):
    """
    Print error messages in a consistent format.
    
    Args:
        error_message (str): A description of the error.
        error (Exception, optional): The exception object, if available.
    """
    print_colored(f"Error: {error_message}", TOOL_COLOR)
    if error:
        print_colored(f"Details: {str(error)}", TOOL_COLOR)

def print_colored(text: str, color: str) -> None:
    """Print text in the specified color."""
    print(f"{color}{text}{Style.RESET_ALL}")

def update_system_prompt(current_iteration: int = None, max_iterations: int = None) -> str:
    """Update the system prompt based on the current state of the conversation."""
    global automode
    automode_status = "You are currently in automode." if automode else "You are not in automode."
    iteration_info = ""
    if current_iteration is not None and max_iterations is not None:
        iteration_info = f"You are currently on iteration {current_iteration} out of {max_iterations} in automode. "
        iteration_info += f"The maximum token limit for this automode session is {MAX_CONTINUATION_TOKENS}."
    else:
        iteration_info = "You are not currently in automode."
    return system_prompt.format(automode_status=automode_status, iteration_info=iteration_info)

def chat_with_claude(user_input: str, image_path: str = None, current_iteration: int = None, max_iterations: int = None) -> Tuple[str, bool]:
    """Process user input and generate a response using the selected AI model."""
    global conversation_history, automode, default_model, clients
    
    input_tokens = count_tokens(user_input)
    current_system_prompt = update_system_prompt(current_iteration, max_iterations)
    system_prompt_tokens = count_tokens(current_system_prompt)
    
    messages = [msg for msg in conversation_history if msg['role'] != 'system']
    
    if image_path:
        print_colored(f"Processing image at path: {image_path}", TOOL_COLOR)
        image_base64 = encode_image_to_base64(image_path)
        
        if image_base64.startswith("Error"):
            print_colored(f"Error encoding image: {image_base64}", TOOL_COLOR)
            update_token_usage(input_tokens, 0, input_tokens, system_prompt_tokens, 0)
            return "I'm sorry, there was an error processing the image. Please try again.", False

        image_message = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64
                    }
                },
                {
                    "type": "text",
                    "text": f"User input for image: {user_input}"
                }
            ]
        }
        messages.append(image_message)
        print_colored("Image message added to messages", TOOL_COLOR)
    else:
        messages.append({"role": "user", "content": user_input})
    
    history_tokens = sum(count_tokens(str(msg.get('content', ''))) for msg in messages)
    
    try:
        if not isinstance(default_model, dict) or 'provider' not in default_model or 'name' not in default_model:
            raise ValueError("Invalid default_model structure")
        
        provider = default_model['provider']
        model_name = default_model['name']
        
        if provider not in clients:
            raise ValueError(f"No client found for provider: {provider}")
        
        client = clients[provider]
        
        # Get the model data from AIModelSelector
        model_data = AIModelSelector.get_model("text_models", provider, model_name)
        
        # Prepare common parameters
        common_params = {
            "model": model_name,
            "messages": [{"role": "system", "content": current_system_prompt}] + messages,
        }
        
        # Add provider-specific parameters and make API call
        if provider == "groq":
            response = client.chat.completions.create(**common_params)
        elif provider == "openai":
            response = client.ChatCompletion.create(**common_params)
        elif provider == "anthropic":
            common_params.update({
                "max_tokens": model_data['max_tokens'],
                "tools": tools,
                "tool_choice": {"type": "auto"}
            })
            response = client.messages.create(**common_params)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Process the response based on the provider
        assistant_response = ""
        exit_continuation = False
        
        if provider in ["groq", "openai"]:
            assistant_response = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens
            if CONTINUATION_EXIT_PHRASE in assistant_response:
                exit_continuation = True
        elif provider == "anthropic":
            for content_block in response.content:
                if content_block.type == "text":
                    assistant_response += content_block.text
                    print_colored(f"\nClaude: {content_block.text}", CLAUDE_COLOR)
                    if CONTINUATION_EXIT_PHRASE in content_block.text:
                        exit_continuation = True
                elif content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_use_id = content_block.id
                    
                    print_colored(f"\nTool Used: {tool_name}", TOOL_COLOR)
                    print_colored(f"Tool Input: {tool_input}", TOOL_COLOR)
                    
                    result = execute_tool(tool_name, tool_input)
                    print_colored(f"Tool Result: {result}", RESULT_COLOR)
                    
                    messages.append({"role": "assistant", "content": [content_block]})
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": result
                            }
                        ]
                    })
                    
                    try:
                        tool_response = client.messages.create(**common_params)
                        
                        for tool_content_block in tool_response.content:
                            if tool_content_block.type == "text":
                                assistant_response += tool_content_block.text
                                print_colored(f"\nClaude: {tool_content_block.text}", CLAUDE_COLOR)
                        
                        tool_input_tokens = count_tokens(result)
                        tool_output_tokens = client.get_output_tokens(tool_response)
                        tool_total_tokens = tool_input_tokens + tool_output_tokens + system_prompt_tokens + history_tokens
                        update_token_usage(tool_input_tokens, tool_output_tokens, tool_total_tokens, system_prompt_tokens, history_tokens)
                        
                    except Exception as e:
                        print_colored(f"Error in tool response: {str(e)}", TOOL_COLOR)
                        assistant_response += "\nI encountered an error while processing the tool result. Please try again."
            
            output_tokens = response.usage.output_tokens
        
    except Exception as e:
        error_msg = f"Error calling AI API: {type(e).__name__} - {str(e)}"
        print_colored(error_msg, TOOL_COLOR)
        total_tokens = input_tokens + system_prompt_tokens + history_tokens
        update_token_usage(input_tokens, 0, total_tokens, system_prompt_tokens, history_tokens)
        return f"I'm sorry, there was an error communicating with the AI: {str(e)}. Please try again or check the configuration.", False
    
    total_tokens = input_tokens + output_tokens + system_prompt_tokens + history_tokens
    update_token_usage(input_tokens, output_tokens, total_tokens, system_prompt_tokens, history_tokens)
    
    if assistant_response:
        messages.append({
            "role": "assistant", 
            "content": assistant_response,
        })
    
    conversation_history = messages
    
    return assistant_response, exit_continuation


def process_and_display_response(response: str) -> None:
    """Process and display the AI's response, handling code blocks and regular text."""
    processed_response = process_response(response)
    for content_type, content in processed_response:
        if content_type == 'text':
            print_colored(content, CLAUDE_COLOR)
        elif content_type == 'code':
            language, code = content
            formatted_code = format_code(code, language)
            print(formatted_code)

def process_response(response: str) -> List[Tuple[str, str]]:
    """Process the AI's response, separating code blocks from regular text."""
    processed_response = []
    parts = response.split("```")
    
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                processed_response.append(('text', part.strip()))
        else:
            lines = part.split('\n')
            language = lines[0].strip() if lines else ""
            code = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            if language and code:
                processed_response.append(('code', (language, code)))
            elif code:
                processed_response.append(('code', ('', code)))
            else:
                processed_response.append(('text', part))
    
    return processed_response

def format_code(code: str, language: str) -> str:
    """Format code with syntax highlighting."""
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import TerminalFormatter
    import pygments.util

    try:
        lexer = get_lexer_by_name(language, stripall=True)
        formatter = TerminalFormatter()
        return highlight(code, lexer, formatter)
    except pygments.util.ClassNotFound:
        return f"Code (language: {language}):\n{code}"

def display_token_usage_summary():
    """Display a summary of token usage."""
    usage = get_token_usage()
    usage_display = display_token_usage(usage, is_summary=True)
    print_colored(usage_display, TOOL_COLOR)

def change_model():
    """Allow the user to change the current AI model."""
    global default_model
    print_colored("Available models:", TOOL_COLOR)
    for provider, models in AIModelSelector.list_models("text_models").items():
        print_colored(f"Provider: {provider}", TOOL_COLOR)
        for model_name in models:
            print_colored(f"  - {model_name}", TOOL_COLOR)
    
    provider = input(f"{USER_COLOR}Enter the provider name: {Style.RESET_ALL}")
    model_name = input(f"{USER_COLOR}Enter the model name: {Style.RESET_ALL}")
    
    try:
        model_data = AIModelSelector.get_model("text_models", provider, model_name)
        default_model = {
            'provider': provider,
            'name': model_name,
            'data': model_data
        }
        print_colored(f"Model changed to {model_name} from provider {provider}.", TOOL_COLOR)
    except ValueError as e:
        print_colored(f"Error changing model: {str(e)}", TOOL_COLOR)
        print_colored(f"Keeping the current model: {default_model['name']} from provider {default_model['provider']}", TOOL_COLOR)

def main():
    """Main function to run the Claude Engineer chat application."""
    global automode, conversation_history, default_model
    print_colored("Welcome to the Claude Engineer Chat with Image Support!", CLAUDE_COLOR)
    print_colored("Type 'exit' to end the conversation.", CLAUDE_COLOR)
    print_colored("Type 'image' to include an image in your message.", CLAUDE_COLOR)
    print_colored("Type 'automode [number]' to enter Autonomous mode with a specific number of iterations.", CLAUDE_COLOR)
    print_colored("Type 'token' to see the token usage summary.", CLAUDE_COLOR)
    print_colored("Type 'model' to change the current model.", CLAUDE_COLOR)
    print_colored("While in automode, press Ctrl+C at any time to exit automode to return to regular chat.", CLAUDE_COLOR)
    
    while True:
        try:
            user_input = input(f"\n{USER_COLOR}You: {Style.RESET_ALL}")
            
            if user_input.lower() == 'exit':
                display_token_usage_summary()
                print_colored("Thank you for chatting. Goodbye!", CLAUDE_COLOR)
                break
            
            if user_input.lower() == 'token':
                display_token_usage_summary()
                continue
            
            if user_input.lower() == 'model':
                change_model()
                continue
            
            if user_input.lower() == 'image':
                image_path = input(f"{USER_COLOR}Drag and drop your image here: {Style.RESET_ALL}").strip().replace("'", "")
                
                if os.path.isfile(image_path):
                    user_input = input(f"{USER_COLOR}You (prompt for image): {Style.RESET_ALL}")
                    response, _ = chat_with_claude(user_input, image_path)
                    process_and_display_response(response)
                else:
                    print_colored("Invalid image path. Please try again.", CLAUDE_COLOR)
                    continue
            elif user_input.lower().startswith('automode'):
                try:
                    parts = user_input.split()
                    if len(parts) > 1 and parts[1].isdigit():
                        max_iterations = int(parts[1])
                    else:
                        max_iterations = MAX_CONTINUATION_ITERATIONS
                    
                    automode = True
                    print_colored(f"Entering automode with {max_iterations} iterations. Press Ctrl+C to exit automode at any time.", TOOL_COLOR)
                    user_input = input(f"\n{USER_COLOR}You: {Style.RESET_ALL}")
                    
                    iteration_count = 0
                    total_tokens = 0
                    try:
                        while automode and iteration_count < max_iterations and total_tokens < MAX_CONTINUATION_TOKENS:
                            response, exit_continuation = chat_with_claude(
                                user_input, 
                                current_iteration=iteration_count+1, 
                                max_iterations=max_iterations
                            )
                            process_and_display_response(response)
                            
                            usage = get_token_usage()
                            usage_display = display_token_usage(usage['conversation_tokens'][-1])
                            print_colored(usage_display, TOOL_COLOR)
                            
                            total_tokens += usage['conversation_tokens'][-1]['total_tokens']
                            
                            if exit_continuation or CONTINUATION_EXIT_PHRASE in response:
                                print_colored("Automode completed.", TOOL_COLOR)
                                automode = False
                            elif total_tokens >= MAX_CONTINUATION_TOKENS:
                                print_colored("Maximum token limit reached. Exiting automode.", TOOL_COLOR)
                                automode = False
                            else:
                                print_colored(f"Continuation iteration {iteration_count + 1} completed.", TOOL_COLOR)
                                print_colored(f"Total tokens used: {total_tokens}", TOOL_COLOR)
                                print_colored(f"Tokens remaining: {MAX_CONTINUATION_TOKENS - total_tokens}", TOOL_COLOR)
                                print_colored("Press Ctrl+C to exit automode.", TOOL_COLOR)
                                user_input = "Continue with the next step."
                            
                            iteration_count += 1
                            
                            if iteration_count >= max_iterations:
                                print_colored("Max iterations reached. Exiting automode.", TOOL_COLOR)
                                automode = False
                    except KeyboardInterrupt:
                        print_colored("\nAutomode interrupted by user. Exiting automode.", TOOL_COLOR)
                        automode = False
                        if conversation_history and conversation_history[-1]["role"] == "user":
                            conversation_history.append({"role": "assistant", "content": "Automode interrupted. How can I assist you further?"})
                except KeyboardInterrupt:
                    print_colored("\nAutomode interrupted by user. Exiting automode.", TOOL_COLOR)
                    automode = False
                    if conversation_history and conversation_history[-1]["role"] == "user":
                        conversation_history.append({"role": "assistant", "content": "Automode interrupted. How can I assist you further?"})
                
                print_colored("Exited automode. Returning to regular chat.", TOOL_COLOR)
            else:
                response, _ = chat_with_claude(user_input)
                process_and_display_response(response)
                
                usage = get_token_usage()
                usage_display = display_token_usage(usage['conversation_tokens'][-1])
                print_colored(usage_display, TOOL_COLOR)
                
        except KeyboardInterrupt:
            print_colored("\nKeyboard interrupt detected. Exiting current mode.", TOOL_COLOR)
            automode = False
        except Exception as e:
            handle_error("Unexpected error in main loop", e)
    
    print_colored("Thank you for using Claude Engineer. Goodbye!", CLAUDE_COLOR)

if __name__ == "__main__":
    try:
        # Initialize configuration
        config = Config()

        # Initialize clients using the validated API keys from config
        for api_name, api_key in config.valid_apis.items():
            try:
                if api_name == "tavily":
                    tavily_client = TavilyClient(api_key=api_key)
                    print("Tavily client initialized successfully.")
                else:
                    clients[api_name] = AIClientFactory.get_client(api_name)
                    print(f"{api_name.capitalize()} client initialized successfully.")
            except Exception as e:
                print(f"Warning: Failed to initialize {api_name} client. Error: {str(e)}")

        if not clients:
            raise ValueError("No valid API keys found for AI clients.")

        if tavily_client is None:
            print("Warning: Tavily client not initialized. Web search functionality will be unavailable.")

        # Dynamically select the default model
        default_model = None
        for model_type in ["text_models"]:
            for provider in config.valid_apis.keys():
                if provider in clients:
                    available_model = AIModelSelector.get_available_model(model_type, provider)
                    if available_model:
                        default_model = {
                            'provider': provider,
                            'name': available_model
                        }
                        print(f"Default model set to {available_model} from provider {provider}.")
                        break
            if default_model:
                break

        if default_model is None:
            raise ValueError("No valid text models found for any provider.")
        
        main()
    except Exception as e:
        handle_error("Critical error in main function", e)
    finally:
        print_colored("Claude Engineer shutting down.", CLAUDE_COLOR)
