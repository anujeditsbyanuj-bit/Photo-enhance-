import cv2
import numpy as np
from PIL import Image, ImageEnhance
import logging

log = logging.getLogger(__name__)


class Relight:
    """
    AI Relighting — studio-quality lighting presets.
    Every method: PIL Image → PIL Image.
    """

    # ──────────────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _radial_mask(
        h: int, w: int,
        cx_r: float = 0.5, cy_r: float = 0.3,
        inner: float = 0.0, outer: float = 0.75
    ) -> np.ndarray:
        """
        Smooth radial mask 1.0 at centre → 0.0 at edge.
        cx_r, cy_r: centre as ratio of w / h.
        """
        Y, X = np.ogrid[:h, :w]
        cx, cy = w * cx_r, h * cy_r
        dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        r    = np.sqrt(w ** 2 + h ** 2) * outer
        mask = 1.0 - np.clip((dist - r * inner) / (r * (1 - inner)), 0, 1)
        return mask.astype(np.float32)

    @staticmethod
    def _vignette(
        arr: np.ndarray,
        strength: float = 0.55,
        cx_r: float = 0.5, cy_r: float = 0.5
    ) -> np.ndarray:
        h, w  = arr.shape[:2]
        Y, X  = np.ogrid[:h, :w]
        cx, cy = w * cx_r, h * cy_r
        dist  = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        mx    = np.sqrt(cx ** 2 + cy ** 2)
        vig   = 1.0 - strength * (dist / mx)
        vig   = np.clip(vig, 0, 1).astype(np.float32)
        out   = arr.astype(np.float32)
        for c in range(3):
            out[:, :, c] *= vig
        return np.clip(out, 0, 255).astype(np.uint8)

    @staticmethod
    def _tint(arr: np.ndarray, rgb_mul: tuple) -> np.ndarray:
        out = arr.astype(np.float32)
        for c, m in enumerate(rgb_mul):
            out[:, :, c] = np.clip(out[:, :, c] * m, 0, 255)
        return out.astype(np.uint8)

    # ──────────────────────────────────────────────────────────────────────
    # PRESETS
    # ──────────────────────────────────────────────────────────────────────

    @classmethod
    def studio_white(cls, img: Image.Image) -> Image.Image:
        """Clean white-background studio fill light."""
        arr  = np.array(img.convert("RGB"))
        h, w = arr.shape[:2]

        # Soft top-centre fill
        mask = cls._radial_mask(h, w, cx_r=0.5, cy_r=0.0, outer=0.9)
        lit  = arr.astype(np.float32)
        for c in range(3):
            lit[:, :, c] += mask * 30          # add light (+30 max)
        lit = np.clip(lit, 0, 255).astype(np.uint8)

        # Gentle vignette to focus on subject
        lit = cls._vignette(lit, strength=0.30)

        out = Image.fromarray(lit)
        out = ImageEnhance.Contrast(out).enhance(1.15)
        return out

    @classmethod
    def golden_hour(cls, img: Image.Image) -> Image.Image:
        """Warm sunset / golden-hour glow from the right."""
        arr  = np.array(img.convert("RGB"))
        h, w = arr.shape[:2]

        # Horizontal gradient: warm on right side
        grad = np.linspace(0.80, 1.20, w, dtype=np.float32)
        grad = np.tile(grad, (h, 1))

        arr  = arr.astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * grad * 1.18, 0, 255)  # R++
        arr[:, :, 1] = np.clip(arr[:, :, 1] * grad * 1.00, 0, 255)  # G~
        arr[:, :, 2] = np.clip(arr[:, :, 2] * grad * 0.72, 0, 255)  # B--
        arr = arr.astype(np.uint8)

        arr = cls._vignette(arr, strength=0.35, cx_r=0.8, cy_r=0.5)

        out = Image.fromarray(arr)
        out = ImageEnhance.Color(out).enhance(1.35)
        return out

    @classmethod
    def dramatic_shadow(cls, img: Image.Image) -> Image.Image:
        """Hard side-key light with deep shadows (Rembrandt style)."""
        arr  = np.array(img.convert("RGB"))
        h, w = arr.shape[:2]

        # Light from upper-left
        mask = cls._radial_mask(h, w, cx_r=0.0, cy_r=0.0, inner=0.1, outer=0.9)
        lit  = arr.astype(np.float32)
        for c in range(3):
            lit[:, :, c] *= (0.35 + mask * 0.85)   # shadow → lit range
        lit = np.clip(lit, 0, 255).astype(np.uint8)

        out = Image.fromarray(lit)
        out = ImageEnhance.Contrast(out).enhance(1.40)
        return out

    @classmethod
    def soft_beauty(cls, img: Image.Image) -> Image.Image:
        """Butterfly / clamshell light for beauty / fashion."""
        arr  = np.array(img.convert("RGB"))

        # Bilateral smoothing (skin)
        smooth = cv2.bilateralFilter(arr, d=12, sigmaColor=80, sigmaSpace=80)
        arr    = cv2.addWeighted(arr, 0.3, smooth, 0.7, 0)

        h, w = arr.shape[:2]
        # Top-centre overhead fill
        mask = cls._radial_mask(h, w, cx_r=0.5, cy_r=0.0, outer=0.80)
        lit  = arr.astype(np.float32)
        for c in range(3):
            lit[:, :, c] += mask * 18
        lit = np.clip(lit, 0, 255).astype(np.uint8)

        out = Image.fromarray(lit)
        out = ImageEnhance.Brightness(out).enhance(1.07)
        out = ImageEnhance.Color(out).enhance(1.10)
        return out

    @classmethod
    def neon_night(cls, img: Image.Image) -> Image.Image:
        """Cyberpunk neon-blue / magenta club light."""
        arr  = np.array(img.convert("RGB"))
        arr  = cls._tint(arr, (1.30, 0.50, 1.60))   # magenta-blue

        h, w = arr.shape[:2]
        mask = cls._radial_mask(h, w, cx_r=0.5, cy_r=0.5, outer=0.70)
        lit  = arr.astype(np.float32)
        for c in range(3):
            lit[:, :, c] *= (0.40 + mask * 0.70)
        lit = np.clip(lit, 0, 255).astype(np.uint8)
        lit = cls._vignette(lit, strength=0.60)

        out = Image.fromarray(lit)
        out = ImageEnhance.Contrast(out).enhance(1.45)
        out = ImageEnhance.Color(out).enhance(1.60)
        return out

    @classmethod
    def moonlight(cls, img: Image.Image) -> Image.Image:
        """Cool, desaturated moonlight from above."""
        arr = np.array(img.convert("RGB"))
        arr = cls._tint(arr, (0.75, 0.85, 1.20))    # cold blue cast

        h, w = arr.shape[:2]
        mask = cls._radial_mask(h, w, cx_r=0.5, cy_r=0.0, outer=0.85)
        lit  = arr.astype(np.float32)
        for c in range(3):
            lit[:, :, c] *= (0.45 + mask * 0.65)
        lit = np.clip(lit, 0, 255).astype(np.uint8)
        lit = cls._vignette(lit, strength=0.50)

        out = Image.fromarray(lit)
        out = ImageEnhance.Contrast(out).enhance(1.20)
        return out

    @classmethod
    def warm_candlelight(cls, img: Image.Image) -> Image.Image:
        """Intimate warm candlelight from below-centre."""
        arr  = np.array(img.convert("RGB"))
        arr  = cls._tint(arr, (1.30, 0.90, 0.55))   # amber

        h, w = arr.shape[:2]
        mask = cls._radial_mask(h, w, cx_r=0.5, cy_r=0.85, outer=0.75)
        lit  = arr.astype(np.float32)
        for c in range(3):
            lit[:, :, c] *= (0.30 + mask * 0.85)
        lit = np.clip(lit, 0, 255).astype(np.uint8)
        lit = cls._vignette(lit, strength=0.55)

        out = Image.fromarray(lit)
        out = ImageEnhance.Contrast(out).enhance(1.25)
        return out

    @classmethod
    def forest_green(cls, img: Image.Image) -> Image.Image:
        """Dappled natural green / forest light."""
        arr = np.array(img.convert("RGB"))
        arr = cls._tint(arr, (0.80, 1.25, 0.75))

        h, w = arr.shape[:2]
        mask = cls._radial_mask(h, w, cx_r=0.4, cy_r=0.2, outer=0.80)
        lit  = arr.astype(np.float32)
        for c in range(3):
            lit[:, :, c] *= (0.50 + mask * 0.65)
        lit = np.clip(lit, 0, 255).astype(np.uint8)
        lit = cls._vignette(lit, strength=0.40)

        out = Image.fromarray(lit)
        out = ImageEnhance.Color(out).enhance(1.20)
        return out
