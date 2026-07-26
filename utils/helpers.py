import os
import io
import uuid
import logging
from PIL import Image
from config import TEMP_DIR, JPEG_QUALITY

logger = logging.getLogger(__name__)

def ensure_temp_dir():
    """Temp directory banao"""
    os.makedirs(TEMP_DIR, exist_ok=True)

def get_temp_path(extension="jpg"):
    """Unique temp file path generate karo"""
    ensure_temp_dir()
    filename = f"{uuid.uuid4().hex}.{extension}"
    return os.path.join(TEMP_DIR, filename)

def image_to_bytes(img: Image.Image, fmt="JPEG") -> io.BytesIO:
    """PIL Image → BytesIO"""
    output = io.BytesIO()
    if fmt == "PNG":
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        img.save(output, format='PNG')
    else:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(output, format='JPEG', quality=JPEG_QUALITY)
    output.seek(0)
    return output

def bytes_to_image(data: bytes) -> Image.Image:
    """Bytes → PIL Image"""
    return Image.open(io.BytesIO(data))

def cleanup_file(path: str):
    """Temp file delete karo"""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.warning(f"Cleanup error: {e}")

def format_size(size_bytes: int) -> str:
    """Bytes to readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024*1024):.1f} MB"

def get_image_info(img: Image.Image) -> str:
    """Image ka info string"""
    w, h = img.size
    return (
        f"📊 *Image Info:*\n"
        f"• Size: `{w} × {h}` px\n"
        f"• Mode: `{img.mode}`\n"
        f"• Megapixels: `{(w*h)/1_000_000:.2f} MP`"
    )
