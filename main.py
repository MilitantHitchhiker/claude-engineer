import os
from datetime import datetime
import json
from colorama import init, Fore, Style
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
from tavily import TavilyClient
import pygments.util
import base64
from PIL import Image
import io
import re
from anthropic import Anthropic
import tiktoken

# Initialize colorama
init()

# Color constants
USER_COLOR = Fore.WHITE
CLAUDE_COLOR = Fore.BLUE
TOOL_COLOR = Fore.YELLOW
RESULT_COLOR = Fore.GREEN

# Add these constants at the top of the file
CONTINUATION_EXIT_PHRASE = "AUTOMODE_COMPLETE"
MAX_CONTINUATION_ITERATIONS = 25

# Initialize the Anthropic client
client = Anthropic(api_key=os.environ("ANTHROPIC_API_KEY"))

# Initialize the Tavily client
tavily = TavilyClient(api_key=os.environ("TAVILY_API_KEY"))

# Set up the conversation memory
conversation_history = []

# automode flag
automode = False

# Global variable to store token usage
token_usage = {
    "total_tokens": 0,
    "conversation_tokens": []
}

# Initialize the tokenizer
try:
    tokenizer = tiktoken.get_encoding("cl100k_base")  # This is the encoding used by Claude
except KeyError:
    print("Warning: cl100k_base encoding not found. Falling back to p50k_base.")
    tokenizer = tiktoken.get_encoding("p50k_base")

# System prompt
system_prompt = """
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
10. IMPORTANT!! You NEVER remove existing code if doesnt require to be changed or removed, never use comments  like # ... (keep existing code) ... or # ... (rest of the code) ... etc, you only add new code or remove it or EDIT IT.
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
- Use the write_to_file tool to implement changes.

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

def count_tokens(text):
    return len(tokenizer.encode(text))

def update_token_usage(input_tokens, output_tokens, total_tokens, system_tokens, history_tokens):
    global token_usage
    token_usage["total_tokens"] += total_tokens
    token_usage["conversation_tokens"].append({
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "system_tokens": system_tokens,
        "history_tokens": history_tokens,
        "total_tokens": total_tokens
    })

def update_system_prompt(current_iteration=None, max_iterations=None):
    global system_prompt
    automode_status = "You are currently in automode." if automode else "You are not in automode."
    iteration_info = ""
    if current_iteration is not None and max_iterations is not None:
        iteration_info = f"You are currently on iteration {current_iteration} out of {max_iterations} in automode."
    return system_prompt.format(automode_status=automode_status, iteration_info=iteration_info)

def print_colored(text, color):
    print(f"{color}{text}{Style.RESET_ALL}")

def print_code(code, language):
    try:
        lexer = get_lexer_by_name(language, stripall=True)
        formatted_code = highlight(code, lexer, TerminalFormatter())
        print(formatted_code)
    except pygments.util.ClassNotFound:
        print_colored(f"Code (language: {language}):\n{code}", CLAUDE_COLOR)

def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder created: {path}"
    except Exception as e:
        return f"Error creating folder: {str(e)}"

def create_file(path, content=""):
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"File created: {path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def write_to_file(path, content):
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"Content written to file: {path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

def read_file(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(path="."):
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def tavily_search(query):
    try:
        response = tavily.qna_search(query=query, search_depth="advanced")
        return response
    except Exception as e:
        return f"Error performing search: {str(e)}"

tools = [
    {
        "name": "create_folder",
        "description": "Create a new folder at the specified path. Use this when you need to create a new directory in the project structure.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path where the folder should be created"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "create_file",
        "description": "Create a new file at the specified path with optional content. Use this when you need to create a new file in the project structure.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path where the file should be created"
                },
                "content": {
                    "type": "string",
                    "description": "The initial content of the file (optional)"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_to_file",
        "description": "Write content to an existing file at the specified path. Use this when you need to add or update content in an existing file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the file to write to"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the file to read"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_files",
        "description": "List all files and directories in the root folder where the script is running. Use this when you need to see the contents of the current directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the folder to list (default: current directory)"
                }
            }
        }
    },
    {
        "name": "tavily_search",
        "description": "Perform a web search using Tavily API to get up-to-date information or additional context. Use this when you need current information or feel a search could provide a better answer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    }
]

def execute_tool(tool_name, tool_input):
    if tool_name == "create_folder":
        return create_folder(tool_input["path"])
    elif tool_name == "create_file":
        return create_file(tool_input["path"], tool_input.get("content", ""))
    elif tool_name == "write_to_file":
        return write_to_file(tool_input["path"], tool_input.get("content", ""))
    elif tool_name == "read_file":
        return read_file(tool_input["path"])
    elif tool_name == "list_files":
        return list_files(tool_input.get("path", "."))
    elif tool_name == "tavily_search":
        return tavily_search(tool_input["query"])
    else:
        return f"Unknown tool: {tool_name}"

def encode_image_to_base64(image_path):
    try:
        with Image.open(image_path) as img:
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.DEFAULT_STRATEGY)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    except Exception as e:
        return f"Error encoding image: {str(e)}"

def parse_goals(response):
    goals = re.findall(r'Goal \d+: (.+)', response)
    return goals

def execute_goals(goals):
    global automode
    for i, goal in enumerate(goals, 1):
        print_colored(f"\nExecuting Goal {i}: {goal}", TOOL_COLOR)
        response, _ = chat_with_claude(f"Continue working on goal: {goal}")
        if CONTINUATION_EXIT_PHRASE in response:
            automode = False
            print_colored("Exiting automode.", TOOL_COLOR)
            break

def chat_with_claude(user_input, image_path=None, current_iteration=None, max_iterations=None):
    global conversation_history, automode
    
    # Count input tokens
    input_tokens = count_tokens(user_input)
    
    # Update system prompt
    current_system_prompt = update_system_prompt(current_iteration, max_iterations)
    
    # Check if we need to add or update the system message
    if not conversation_history or conversation_history[0]['role'] != 'system':
        conversation_history.insert(0, {"role": "system", "content": current_system_prompt})
    else:
        conversation_history[0]['content'] = current_system_prompt
    
    # Count system prompt tokens
    system_prompt_tokens = count_tokens(current_system_prompt)
    
    # Count conversation history tokens
    history_tokens = sum(count_tokens(str(msg.get('content', ''))) for msg in conversation_history[1:])
    
    if image_path:
        print_colored(f"Processing image at path: {image_path}", TOOL_COLOR)
        image_base64 = encode_image_to_base64(image_path)
        
        if image_base64.startswith("Error"):
            print_colored(f"Error encoding image: {image_base64}", TOOL_COLOR)
            update_token_usage(input_tokens, 0, input_tokens, system_prompt_tokens, history_tokens)
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
        conversation_history.append(image_message)
        print_colored("Image message added to conversation history", TOOL_COLOR)
    else:
        conversation_history.append({"role": "user", "content": user_input})
    
    messages = conversation_history.copy()
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            messages=messages,
            tools=tools,
            tool_choice={"type": "auto"}
        )
        
        # Extract token usage from the response
        output_tokens = response.usage.output_tokens
        
    except Exception as e:
        print_colored(f"Error calling Claude API: {str(e)}", TOOL_COLOR)
        total_tokens = input_tokens + system_prompt_tokens + history_tokens
        update_token_usage(input_tokens, 0, total_tokens, system_prompt_tokens, history_tokens)
        return "I'm sorry, there was an error communicating with the AI. Please try again.", False
    
    # Calculate total tokens and update token usage
    total_tokens = input_tokens + output_tokens + system_prompt_tokens + history_tokens
    update_token_usage(input_tokens, output_tokens, total_tokens, system_prompt_tokens, history_tokens)
    
    assistant_response = ""
    exit_continuation = False
    
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
            
            conversation_history.append({"role": "assistant", "content": [content_block]})
            conversation_history.append({
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
                tool_response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4000,
                    messages=[msg for msg in conversation_history if msg.get('content')],
                    tools=tools,
                    tool_choice={"type": "auto"}
                )
                
                for tool_content_block in tool_response.content:
                    if tool_content_block.type == "text":
                        assistant_response += tool_content_block.text
                        print_colored(f"\nClaude: {tool_content_block.text}", CLAUDE_COLOR)
                
                # Update token usage for tool response
                tool_input_tokens = count_tokens(result)
                tool_output_tokens = tool_response.usage.output_tokens
                tool_total_tokens = tool_input_tokens + tool_output_tokens + system_prompt_tokens + history_tokens
                update_token_usage(tool_input_tokens, tool_output_tokens, tool_total_tokens, system_prompt_tokens, history_tokens)
                
            except Exception as e:
                print_colored(f"Error in tool response: {str(e)}", TOOL_COLOR)
                assistant_response += "\nI encountered an error while processing the tool result. Please try again."
    
    if assistant_response:
        conversation_history.append({
            "role": "assistant", 
            "content": assistant_response,
        })
    
    return assistant_response, exit_continuation

def process_and_display_response(response):
    if response.startswith("Error") or response.startswith("I'm sorry"):
        print_colored(response, TOOL_COLOR)
    else:
        if "```" in response:
            parts = response.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    print_colored(part, CLAUDE_COLOR)
                else:
                    lines = part.split('\n')
                    language = lines[0].strip() if lines else ""
                    code = '\n'.join(lines[1:]) if len(lines) > 1 else ""
                    
                    if language and code:
                        print_code(code, language)
                    elif code:
                        print_colored(f"Code:\n{code}", CLAUDE_COLOR)
                    else:
                        print_colored(part, CLAUDE_COLOR)
        else:
            print_colored(response, CLAUDE_COLOR)

def chat_with_claude(user_input, image_path=None, current_iteration=None, max_iterations=None):
    global conversation_history, automode
    
    # Count input tokens
    input_tokens = count_tokens(user_input)
    
    # Update system prompt
    current_system_prompt = update_system_prompt(current_iteration, max_iterations)
    
    # Count system prompt tokens
    system_prompt_tokens = count_tokens(current_system_prompt)
    
    # Prepare messages, excluding any previous system messages
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
    
    # Count conversation history tokens (excluding system prompt)
    history_tokens = sum(count_tokens(str(msg.get('content', ''))) for msg in messages)
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            system=current_system_prompt,
            messages=messages,
            tools=tools,
            tool_choice={"type": "auto"}
        )
        
        # Extract token usage from the response
        output_tokens = response.usage.output_tokens
        
    except Exception as e:
        print_colored(f"Error calling Claude API: {str(e)}", TOOL_COLOR)
        total_tokens = input_tokens + system_prompt_tokens + history_tokens
        update_token_usage(input_tokens, 0, total_tokens, system_prompt_tokens, history_tokens)
        return "I'm sorry, there was an error communicating with the AI. Please try again.", False
    
    # Calculate total tokens and update token usage
    total_tokens = input_tokens + output_tokens + system_prompt_tokens + history_tokens
    update_token_usage(input_tokens, output_tokens, total_tokens, system_prompt_tokens, history_tokens)
    
    assistant_response = ""
    exit_continuation = False
    
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
                tool_response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4000,
                    system=current_system_prompt,
                    messages=messages,
                    tools=tools,
                    tool_choice={"type": "auto"}
                )
                
                for tool_content_block in tool_response.content:
                    if tool_content_block.type == "text":
                        assistant_response += tool_content_block.text
                        print_colored(f"\nClaude: {tool_content_block.text}", CLAUDE_COLOR)
                
                # Update token usage for tool response
                tool_input_tokens = count_tokens(result)
                tool_output_tokens = tool_response.usage.output_tokens
                tool_total_tokens = tool_input_tokens + tool_output_tokens + system_prompt_tokens + history_tokens
                update_token_usage(tool_input_tokens, tool_output_tokens, tool_total_tokens, system_prompt_tokens, history_tokens)
                
            except Exception as e:
                print_colored(f"Error in tool response: {str(e)}", TOOL_COLOR)
                assistant_response += "\nI encountered an error while processing the tool result. Please try again."
    
    if assistant_response:
        messages.append({
            "role": "assistant", 
            "content": assistant_response,
        })
    
    # Update the global conversation_history
    conversation_history = messages
    
    return assistant_response, exit_continuation

def get_token_usage():
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
    if is_summary:
        print_colored("\nToken Usage Summary:", TOOL_COLOR)
    else:
        print_colored("\nTokens used in this interaction:", TOOL_COLOR)
    
    last_message = usage['last_message']
    print_colored(f"  Input:   {last_message['input_tokens']:>6}", TOOL_COLOR)
    print_colored(f"  Output:  {last_message['output_tokens']:>6}", TOOL_COLOR)
    print_colored(f"  System:  {last_message['system_tokens']:>6}", TOOL_COLOR)
    print_colored(f"  History: {last_message['history_tokens']:>6}", TOOL_COLOR)
    print_colored(f"  Total:   {last_message['total_tokens']:>6}", TOOL_COLOR)
    
    if is_summary:
        print_colored(f"Cumulative tokens used: {usage['total_tokens']}", TOOL_COLOR)
        print_colored(f"Average Tokens per Message: {usage['average_tokens_per_message']:.2f}", TOOL_COLOR)

def main():
    global automode, conversation_history
    print_colored("Welcome to the Claude-3.5-Sonnet Engineer Chat with Image Support!", CLAUDE_COLOR)
    print_colored("Type 'exit' to end the conversation.", CLAUDE_COLOR)
    print_colored("Type 'image' to include an image in your message.", CLAUDE_COLOR)
    print_colored("Type 'automode [number]' to enter Autonomous mode with a specific number of iterations.", CLAUDE_COLOR)
    print_colored("Type 'token' to see the token usage summary.", CLAUDE_COLOR)
    print_colored("While in automode, press Ctrl+C at any time to exit the automode to return to regular chat.", CLAUDE_COLOR)
    
    while True:
        user_input = input(f"\n{USER_COLOR}You: {Style.RESET_ALL}")
        
        if user_input.lower() == 'exit':
            usage = get_token_usage()
            if usage['conversation_tokens']:
                display_token_usage(usage['conversation_tokens'][-1])
            print_colored(f"Cumulative tokens used: {usage['total_tokens']}", TOOL_COLOR)
            print_colored(f"Thank you for chatting. Goodbye!", CLAUDE_COLOR)
            break
        
        if user_input.lower() == 'token':
            usage = get_token_usage()
            if usage['conversation_tokens']:
                display_token_usage(usage['conversation_tokens'][-1])
            print_colored(f"Cumulative tokens used: {usage['total_tokens']}", TOOL_COLOR)
            print_colored(f"Average Tokens per Message: {usage['average_tokens_per_message']:.2f}", TOOL_COLOR)
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
                print_colored("Press Ctrl+C at any time to exit the automode loop.", TOOL_COLOR)
                user_input = input(f"\n{USER_COLOR}You: {Style.RESET_ALL}")
                
                iteration_count = 0
                try:
                    while automode and iteration_count < max_iterations:
                        response, exit_continuation = chat_with_claude(user_input, current_iteration=iteration_count+1, max_iterations=max_iterations)
                        process_and_display_response(response)
                        
                        usage = get_token_usage()
                        if usage['conversation_tokens']:
                            display_token_usage(usage['conversation_tokens'][-1])
                        
                        if exit_continuation or CONTINUATION_EXIT_PHRASE in response:
                            print_colored("Automode completed.", TOOL_COLOR)
                            automode = False
                        else:
                            print_colored(f"Continuation iteration {iteration_count + 1} completed.", TOOL_COLOR)
                            print_colored("Press Ctrl+C to exit automode.", TOOL_COLOR)
                            user_input = "Continue with the next step."
                        
                        iteration_count += 1
                        
                        if iteration_count >= max_iterations:
                            print_colored("Max iterations reached. Exiting automode.", TOOL_COLOR)
                            automode = False
                except KeyboardInterrupt:
                    print_colored("\nAutomode interrupted by user. Exiting automode.", TOOL_COLOR)
                    automode = False
                    # Ensure the conversation history ends with an assistant message
                    if conversation_history and conversation_history[-1]["role"] == "user":
                        conversation_history.append({"role": "assistant", "content": "Automode interrupted. How can I assist you further?"})
            except KeyboardInterrupt:
                print_colored("\nAutomode interrupted by user. Exiting automode.", TOOL_COLOR)
                automode = False
                # Ensure the conversation history ends with an assistant message
                if conversation_history and conversation_history[-1]["role"] == "user":
                    conversation_history.append({"role": "assistant", "content": "Automode interrupted. How can I assist you further?"})
            
            print_colored("Exited automode. Returning to regular chat.", TOOL_COLOR)
        else:
            response, _ = chat_with_claude(user_input)
            process_and_display_response(response)
            
            usage = get_token_usage()
            if usage['conversation_tokens']:
                display_token_usage(usage['conversation_tokens'][-1])
            
        print_colored(f"Cumulative tokens used: {usage['total_tokens']}", TOOL_COLOR)

if __name__ == "__main__":
    main()
