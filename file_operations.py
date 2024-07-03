"""
This module handles file and folder operations for the Claude chat application.
It provides functions for creating folders, creating files, writing to files,
reading files, and listing directory contents.
"""

import os
import difflib
from typing import List

def create_folder(path: str) -> str:
    """
    Create a new folder at the specified path.

    Args:
        path (str): The path where the folder should be created.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder created: {path}"
    except Exception as e:
        return f"Error creating folder: {str(e)}"

def create_file(path: str, content: str = "") -> str:
    """
    Create a new file at the specified path with optional content.

    Args:
        path (str): The path where the file should be created.
        content (str, optional): The initial content of the file. Defaults to "".

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"File created: {path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def generate_and_apply_diff(original_content: str, new_content: str, path: str) -> str:
    """
    Generate a diff between original and new content, and apply it to the file.

    Args:
        original_content (str): The original content of the file.
        new_content (str): The new content to be written to the file.
        path (str): The path of the file to be updated.

    Returns:
        str: A message indicating the changes applied or any errors encountered.
    """
    diff = list(difflib.unified_diff(
        original_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
        n=3
    ))
    
    if not diff:
        return "No changes detected."
    
    try:
        with open(path, 'w') as f:
            f.writelines(new_content)
        return f"Changes applied to {path}:\n" + ''.join(diff)
    except Exception as e:
        return f"Error applying changes: {str(e)}"

def write_to_file(path: str, content: str) -> str:
    """
    Write content to a file, creating the file if it doesn't exist.

    Args:
        path (str): The path of the file to write to.
        content (str): The content to write to the file.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                original_content = f.read()
            result = generate_and_apply_diff(original_content, content, path)
        else:
            with open(path, 'w') as f:
                f.write(content)
            result = f"New file created and content written to: {path}"
        return result
    except Exception as e:
        return f"Error writing to file: {str(e)}"

def read_file(path: str) -> str:
    """
    Read the contents of a file.

    Args:
        path (str): The path of the file to read.

    Returns:
        str: The contents of the file or an error message.
    """
    try:
        with open(path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(path: str = ".") -> str:
    """
    List all files and directories in the specified path.

    Args:
        path (str, optional): The path of the folder to list. Defaults to current directory.

    Returns:
        str: A string containing the list of files and directories or an error message.
    """
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"