from file_operations import create_folder, create_file, write_to_file, read_file, list_files
from tavily import TavilyClient
from config import config  # Import the config instance
from typing import Dict, Any, List
import json

# Initialize the Tavily client using the API key from the config instance
tavily_client = TavilyClient(api_key=config.api_keys.get('tavily'))

tools = [
    {
        "name": "create_folder",
        "description": "Create a new folder at the specified path. Use this when you need to create a new directory in the project structure.",
        "parameters": {
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
        "parameters": {
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
        "description": "Write content to a file at the specified path. If the file exists, only the necessary changes will be applied. If the file doesn't exist, it will be created. Always provide the full intended content of the file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the file to write to"
                },
                "content": {
                    "type": "string",
                    "description": "The full content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file.",
        "parameters": {
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
        "parameters": {
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
        "parameters": {
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

def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    try:
        if tool_name == "create_folder":
            return create_folder(tool_input["path"])
        elif tool_name == "create_file":
            return create_file(tool_input["path"], tool_input.get("content", ""))
        elif tool_name == "write_to_file":
            return write_to_file(tool_input["path"], tool_input["content"])
        elif tool_name == "read_file":
            return read_file(tool_input["path"])
        elif tool_name == "list_files":
            return list_files(tool_input.get("path", "."))
        elif tool_name == "tavily_search":
            return tavily_search(tool_input["query"])
        else:
            return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"Error executing tool {tool_name}: {str(e)}"

def tavily_search(query: str) -> str:
    try:
        response = tavily_client.qna_search(query=query, search_depth="advanced")
        return json.dumps(response)
    except Exception as e:
        return f"Error performing search: {str(e)}"

def execute_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call['function']['name']
        tool_arguments = json.loads(tool_call['function']['arguments'])
        result = execute_tool(tool_name, tool_arguments)
        results.append({
            "tool_call_id": tool_call['id'],
            "role": "tool",
            "name": tool_name,
            "content": result
        })