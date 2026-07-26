import numpy as np
from PIL import Image
import cv2
import io
import logging

logger = logging.getLogger(__name__)

class BackgroundRemover:
    """Background Removal - Multiple Methods"""
    
    @staticmethod
    def remove_background_rembg(img: Image.Image) -> Image.Image:
        """Best Quality using rembg AI library"""
        try:
            from rembg import remove
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            
            # Remove background
            output_bytes = remove(img_bytes.read())
            
            result = Image.open(io.BytesIO(output_bytes))
            return result
            
        except ImportError:
            logger.warning("rembg not installed, using fallback")
            return BackgroundRemover.remove_background_grabcut(img)
        except Exception as e:
            logger.error(f"rembg error: {e}")
            return BackgroundRemover.remove_background_grabcut(img)
    
    @staticmethod
    def remove_background_grabcut(img: Image.Image) -> Image.Image:
        """GrabCut algorithm fallback"""
        try:
            img_rgb = np.array(img.convert("RGB"))
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            
            # GrabCut
            mask = np.zeros(img_bgr.shape[:2], np.uint8)
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)
            
            h, w = img_bgr.shape[:2]
            rect = (10, 10, w - 20, h - 20)
            
            cv2.grabCut(
                img_bgr, mask, rect,
                bgd_model, fgd_model,
                5, cv2.GC_INIT_WITH_RECT
            )
            
            mask2 = np.where(
                (mask == 2) | (mask == 0), 0, 1
            ).astype("uint8")
            
            # Apply mask
            result_rgb = img_rgb * mask2[:, :, np.newaxis]
            
            # Create RGBA
            alpha = mask2 * 255
            rgba = np.dstack((result_rgb, alpha))
            
            return Image.fromarray(rgba.astype(np.uint8), "RGBA")
            
        except Exception as e:
            logger.error(f"GrabCut error: {e}")
            return img
    
    @staticmethod
    def add_background_color(
        img: Image.Image,
        color: tuple = (255, 255, 255)
    ) -> Image.Image:
        """Remove bg aur solid color add karo"""
        try:
            bg_removed = BackgroundRemover.remove_background_rembg(img)
            
            # New background
            background = Image.new("RGB", bg_removed.size, color)
            
            if bg_removed.mode == "RGBA":
                background.paste(bg_removed, mask=bg_removed.split()[3])
            else:
                background.paste(bg_removed)
            
            return background
            
        except Exception as e:
            logger.error(f"Add background error: {e}")
            return img
    
    @staticmethod
    def blur_background(img: Image.Image, blur_radius: int = 15) -> Image.Image:
        """Background blur karo (DSLR effect)"""
        try:
            from rembg import remove
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            
            # Get mask
            output_bytes = remove(img_bytes.read())
            fg_img = Image.open(io.BytesIO(output_bytes))
            
            # Blur original
            img_rgb = img.convert("RGB")
            blurred_bg = img_rgb.filter(
                __import__('PIL').ImageFilter.GaussianBlur(radius=blur_radius)
            )
            
            # Combine
            result = blurred_bg.copy()
            if fg_img.mode == "RGBA":
                result.paste(fg_img.convert("RGB"), mask=fg_img.split()[3])
            
            return result
            
        except Exception as e:
            logger.error(f"Blur background error: {e}")
            return img
