import io, os, uuid, logging
from PIL import Image
from config import TEMP_DIR, JPEG_QUALITY

log = logging.getLogger(__name__)

# ── ensure temp dir ──────────────────────────────────────────────────────
os.makedirs(TEMP_DIR, exist_ok=True)


def load_image(data: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(data))
    img.load()
    return img


def to_bytes(img: Image.Image, fmt: str = "JPEG") -> io.BytesIO:
    buf = io.BytesIO()
    if fmt == "PNG":
        img.convert("RGBA").save(buf, "PNG")
    else:
        img.convert("RGB").save(buf, "JPEG", quality=JPEG_QUALITY)
    buf.seek(0)
    return buf


def tmp_path(ext: str = "jpg") -> str:
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.{ext}")


def img_info(img: Image.Image) -> str:
    w, h = img.size
    mp = (w * h) / 1_000_000
    return (
        f"📐 *Resolution:* `{w} × {h} px`\n"
        f"🔢 *Megapixels:* `{mp:.2f} MP`\n"
        f"🎨 *Mode:* `{img.mode}`"
    )
