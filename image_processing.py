"""
This module handles image processing operations for the Claude chat application.
It provides functions for encoding images to base64 format.
"""

import base64
from PIL import Image
import io

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
            img.thumbnail(max_size, Image.DEFAULT_STRATEGY)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    except Exception as e:
        return f"Error encoding image: {str(e)}"