"""
Darleine Abellard
Craft Watermark

Input validation for uploaded images 
(used before any file is passed to other logic)
"""

import io
from PIL import Image, UnidentifiedImageError

MAX_FILE_SIZE_BYTES = 10 * 1024 ** 2  # 10 MB
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

class ValidationError(Exception):
    """
    Raised when an uploaded file fails validation
    """
    pass

def validate_file_size(file_bytes):
    """Confirms the uploaded file doesn't exceed the maximum size.

    Args:
        file_bytes (bytes): the raw contents of the uploaded file

    Raises:
        ValidationError: if the file is larger than 10 MB
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValidationError(
            f"File is too large. Maximum allowed size is "
            f"{MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )
    
def validate_file_extension(filename):
    """Confirms the uploaded file's name ends in an allowed extension.

    Args:
        filename (str): the uploaded file's name

    Raises:
        ValidationError: if the filename's extension isn't allowed
    """
    lowercase_name = filename.lower()
    has_allowed_extension = any(
        lowercase_name.endswith(ext) for ext in ALLOWED_EXTENSIONS
    )
    if not has_allowed_extension:
        raise ValidationError(
            f"Unsupported file type. Allowed types: "
            f"{', '.join(ALLOWED_EXTENSIONS)}"
        )

def validate_is_real_img(file_bytes):
    """Confirms the uploaded file's actual contents are a genuine image.

    Args:
        file_bytes (bytes): the raw contents of the uploaded file

    Raises:
        ValidationError: if the file's contents can't be recognized 
            as an actual image
    """
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
    except UnidentifiedImageError:
        raise ValidationError(
            "This file doesn't look like a valid image. "
            f"Please upload a genuine PNG or JPEG/JPG file."
        )
    except Exception:
        raise ValidationError(
            "This file couldn't be processed as an image."
        )
    
def validation(filename, file_bytes):
    """Runs complete validation check on an uploaded file

    Args:
        filename (str): the uploaded file's name
        file_bytes (bytes): the raw contents of the uploaded file

    Raises:
        ValidationError: if any individual check fails, a message 
            is shown to the user
    """
    validate_file_size(file_bytes)
    validate_file_extension(filename)
    validate_is_real_img(file_bytes)
