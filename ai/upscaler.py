import cv2
import numpy as np
from PIL import Image
import logging

log = logging.getLogger(__name__)


class Upscaler:
    """
    High-quality AI-style upscaling.
    Uses Lanczos resize + iterative unsharp masking.
    """

    @staticmethod
    def _unsharp(arr: np.ndarray, sigma: float, strength: float) -> np.ndarray:
        blur = cv2.GaussianBlur(arr, (0, 0), sigma)
        sharp = cv2.addWeighted(arr, 1 + strength, blur, -strength, 0)
        return np.clip(sharp, 0, 255).astype(np.uint8)

    @classmethod
    def upscale(cls, img: Image.Image, factor: int = 2) -> Image.Image:
        """
        Upscale × factor (2 or 4).
        Pipeline:
          1. Pre-sharpen  (recover edges before resize)
          2. Lanczos resize
          3. Post-sharpen (restore crisp edges)
          4. Mild denoise (remove upscale artefacts)
        """
        if factor not in (2, 4):
            raise ValueError("factor must be 2 or 4")

        arr = np.array(img.convert("RGB"))
        h, w = arr.shape[:2]

        # ── 1. Pre-sharpen ───────────────────────────────────────────────
        arr = cls._unsharp(arr, sigma=0.8, strength=0.5)

        # ── 2. Resize ────────────────────────────────────────────────────
        new_w, new_h = w * factor, h * factor
        arr = cv2.resize(arr, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        # ── 3. Post-sharpen ──────────────────────────────────────────────
        strength = 1.2 if factor == 2 else 1.5
        arr = cls._unsharp(arr, sigma=1.0, strength=strength)

        # ── 4. Mild denoise ──────────────────────────────────────────────
        arr = cv2.fastNlMeansDenoisingColored(arr, None, 4, 4, 7, 21)

        return Image.fromarray(arr)

    @classmethod
    def enlarge(cls, img: Image.Image, target_mp: float = 12.0) -> Image.Image:
        """
        Enlarge to a target megapixel count (default 12 MP).
        Useful for print-ready output.
        """
        w, h  = img.size
        curr  = (w * h) / 1_000_000
        if curr >= target_mp:
            return img          # already big enough

        scale = (target_mp / curr) ** 0.5
        factor = 2 if scale <= 2.5 else 4
        return cls.upscale(img, factor)
