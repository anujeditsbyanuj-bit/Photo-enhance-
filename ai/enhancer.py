import cv2
import numpy as np
from PIL import Image, ImageEnhance
import logging

log = logging.getLogger(__name__)


class Enhancer:
    """
    AI-grade photo enhancement pipeline.
    Every method takes a PIL Image → returns PIL Image.
    """

    # ──────────────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _to_np(img: Image.Image) -> np.ndarray:
        return np.array(img.convert("RGB"))

    @staticmethod
    def _to_pil(arr: np.ndarray) -> Image.Image:
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    @staticmethod
    def _clahe(arr: np.ndarray, clip: float = 2.5) -> np.ndarray:
        """Adaptive contrast on L-channel (LAB space)."""
        lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        cl = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8)).apply(l)
        return cv2.cvtColor(cv2.merge([cl, a, b]), cv2.COLOR_LAB2RGB)

    @staticmethod
    def _unsharp(arr: np.ndarray, sigma: float = 1.0, strength: float = 1.5) -> np.ndarray:
        """Unsharp mask sharpening."""
        blur   = cv2.GaussianBlur(arr, (0, 0), sigma)
        return cv2.addWeighted(arr, 1 + strength, blur, -strength, 0)

    @staticmethod
    def _denoise(arr: np.ndarray, h: int = 8) -> np.ndarray:
        return cv2.fastNlMeansDenoisingColored(arr, None, h, h, 7, 21)

    # ──────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ──────────────────────────────────────────────────────────────────────

    @classmethod
    def auto(cls, img: Image.Image) -> Image.Image:
        """
        Smart auto-enhancement:
        denoise → CLAHE → unsharp → color pop.
        """
        arr = cls._to_np(img)
        arr = cls._denoise(arr, h=6)
        arr = cls._clahe(arr, clip=2.5)
        arr = cls._unsharp(arr, sigma=1.2, strength=1.0)
        out = cls._to_pil(arr)
        out = ImageEnhance.Color(out).enhance(1.12)
        out = ImageEnhance.Brightness(out).enhance(1.04)
        return out

    @classmethod
    def deep_restore(cls, img: Image.Image) -> Image.Image:
        """
        Heavy restoration for degraded / old photos:
        strong denoise → aggressive CLAHE → sharpening → vivid colours.
        """
        arr = cls._to_np(img)
        arr = cls._denoise(arr, h=14)
        arr = cls._clahe(arr, clip=4.0)
        arr = cls._unsharp(arr, sigma=2.0, strength=2.0)
        out = cls._to_pil(arr)
        out = ImageEnhance.Color(out).enhance(1.4)
        out = ImageEnhance.Contrast(out).enhance(1.2)
        return out

    @classmethod
    def portrait_retouch(cls, img: Image.Image) -> Image.Image:
        """
        Skin smoothing + gentle sharpening for portraits.
        Bilateral filter → blend with original → light boost.
        """
        arr  = cls._to_np(img)
        soft = cv2.bilateralFilter(arr, d=12, sigmaColor=80, sigmaSpace=80)
        arr  = cv2.addWeighted(arr, 0.35, soft, 0.65, 0)   # keep texture
        arr  = cls._unsharp(arr, sigma=1.0, strength=0.8)
        out  = cls._to_pil(arr)
        out  = ImageEnhance.Brightness(out).enhance(1.06)
        out  = ImageEnhance.Color(out).enhance(1.08)
        return out

    @classmethod
    def hdr(cls, img: Image.Image) -> Image.Image:
        """
        HDR tone-mapping look:
        detail-enhance → CLAHE → colour & contrast boost.
        """
        arr = cls._to_np(img)
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        bgr = cv2.detailEnhance(bgr, sigma_s=12, sigma_r=0.12)
        arr = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        arr = cls._clahe(arr, clip=3.0)
        out = cls._to_pil(arr)
        out = ImageEnhance.Contrast(out).enhance(1.30)
        out = ImageEnhance.Color(out).enhance(1.35)
        return out

    @classmethod
    def night_fix(cls, img: Image.Image) -> Image.Image:
        """
        Lift dark / under-exposed photos.
        Gamma → denoise → CLAHE → slight warmth.
        """
        arr = cls._to_np(img).astype(np.float32) / 255.0
        arr = np.power(arr, 1 / 2.0) * 255.0          # gamma lift
        arr = cls._denoise(arr.astype(np.uint8), h=10)
        arr = cls._clahe(arr, clip=3.5)
        # add warmth
        arr = arr.astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.05, 0, 255)  # R+
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.93, 0, 255)  # B-
        return cls._to_pil(arr)

    @classmethod
    def denoise_only(cls, img: Image.Image) -> Image.Image:
        arr = cls._to_np(img)
        arr = cls._denoise(arr, h=12)
        return cls._to_pil(arr)

    @classmethod
    def sharpen_only(cls, img: Image.Image) -> Image.Image:
        arr = cls._to_np(img)
        arr = cls._unsharp(arr, sigma=1.5, strength=2.0)
        return cls._to_pil(arr)

    @classmethod
    def vivid(cls, img: Image.Image) -> Image.Image:
        """Boost saturation + contrast for landscape/nature shots."""
        arr = cls._to_np(img)
        arr = cls._clahe(arr, clip=2.0)
        arr = cls._unsharp(arr, sigma=1.0, strength=0.8)
        out = cls._to_pil(arr)
        out = ImageEnhance.Color(out).enhance(1.6)
        out = ImageEnhance.Contrast(out).enhance(1.2)
        return out
