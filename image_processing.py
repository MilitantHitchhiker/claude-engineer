"""
This module handles image processing operations for the Claude chat application.
It provides functions for encoding images to base64 format.
"""

import base64
from PIL import Image
import io
from typing import Dict

def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 format.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded string of the image or an error message.
    """
    try:
        with Image.open(image_path) as img:
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    except Exception as e:
        return f"Error encoding image: {str(e)}"

def get_image_metadata(image_path: str) -> Dict[str, object] | None:
    """
    Get metadata from an image file.

    Args:
        image_path (str): The path to the image file.

    Returns:
        Dict[str, object] | None: A dictionary containing image metadata, or None if an error occurred.
    """
    try:
        with Image.open(image_path) as img:
            metadata = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "info": img.info
            }
            return metadata
    except Exception as e:
        print(f"Error getting image metadata: {str(e)}")
        return None

def resize_image(image_path: str, output_path: str, max_size: tuple[int, int] = (1024, 1024)) -> bool:
    """
    Resize an image while maintaining its aspect ratio.

    Args:
        image_path (str): The path to the input image file.
        output_path (str): The path where the resized image should be saved.
        max_size (tuple[int, int]): The maximum width and height of the resized image.

    Returns:
        bool: True if the image was successfully resized and saved, False otherwise.
    """
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(output_path)
        return True
    except Exception as e:
        print(f"Error resizing image: {str(e)}")
        return False