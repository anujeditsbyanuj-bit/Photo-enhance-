import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io
import logging

logger = logging.getLogger(__name__)

class AIEnhancer:
    """AI Photo Enhancement Class"""
    
    @staticmethod
    def auto_enhance(img: Image.Image) -> Image.Image:
        """Smart Auto Enhancement"""
        try:
            # Convert to numpy
            img_array = np.array(img.convert("RGB"))
            
            # 1. Denoise
            denoised = cv2.fastNlMeansDenoisingColored(
                img_array, None, 10, 10, 7, 21
            )
            
            # 2. CLAHE for contrast
            lab = cv2.cvtColor(denoised, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            enhanced_lab = cv2.merge((cl, a, b))
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
            
            # 3. Sharpening
            kernel = np.array([
                [-1, -1, -1],
                [-1,  9, -1],
                [-1, -1, -1]
            ])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            result = Image.fromarray(sharpened)
            
            # 4. PIL Enhancements
            result = ImageEnhance.Color(result).enhance(1.15)
            result = ImageEnhance.Brightness(result).enhance(1.05)
            
            return result
            
        except Exception as e:
            logger.error(f"Auto enhance error: {e}")
            return img
    
    @staticmethod
    def upscale_image(img: Image.Image, factor: int = 2) -> Image.Image:
        """AI-quality Upscaling using Lanczos"""
        try:
            img_array = np.array(img.convert("RGB"))
            
            # OpenCV super resolution style upscale
            h, w = img_array.shape[:2]
            new_h, new_w = h * factor, w * factor
            
            # Step 1: Initial upscale with INTER_CUBIC
            upscaled = cv2.resize(
                img_array, (new_w, new_h),
                interpolation=cv2.INTER_CUBIC
            )
            
            # Step 2: Sharpen after upscale
            kernel = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ])
            sharpened = cv2.filter2D(upscaled, -1, kernel)
            
            # Step 3: Denoise
            final = cv2.fastNlMeansDenoisingColored(
                sharpened, None, 5, 5, 7, 21
            )
            
            return Image.fromarray(final)
            
        except Exception as e:
            logger.error(f"Upscale error: {e}")
            w, h = img.size
            return img.resize((w * factor, h * factor), Image.LANCZOS)
    
    @staticmethod
    def enhance_portrait(img: Image.Image) -> Image.Image:
        """Portrait-specific enhancement with skin smoothing"""
        try:
            img_array = np.array(img.convert("RGB"))
            
            # Bilateral filter for skin smoothing
            smoothed = cv2.bilateralFilter(img_array, 9, 75, 75)
            
            # Blend original with smoothed (50/50)
            blended = cv2.addWeighted(img_array, 0.4, smoothed, 0.6, 0)
            
            # Enhance brightness slightly
            result = Image.fromarray(blended)
            result = ImageEnhance.Brightness(result).enhance(1.1)
            result = ImageEnhance.Color(result).enhance(1.1)
            
            return result
            
        except Exception as e:
            logger.error(f"Portrait enhance error: {e}")
            return img
    
    @staticmethod
    def hdr_effect(img: Image.Image) -> Image.Image:
        """HDR-like effect"""
        try:
            img_array = np.array(img.convert("RGB"))
            
            # Tone mapping
            img_float = img_array.astype(np.float32) / 255.0
            
            # Gamma correction
            gamma = 1.2
            corrected = np.power(img_float, 1.0 / gamma)
            
            # Increase local contrast
            lab = cv2.cvtColor((corrected * 255).astype(np.uint8), cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            merged = cv2.merge((cl, a, b))
            hdr = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
            
            result = Image.fromarray(hdr)
            result = ImageEnhance.Color(result).enhance(1.3)
            result = ImageEnhance.Contrast(result).enhance(1.2)
            
            return result
            
        except Exception as e:
            logger.error(f"HDR effect error: {e}")
            return img
    
    @staticmethod  
    def night_to_day(img: Image.Image) -> Image.Image:
        """Make dark/night photos look like daytime"""
        try:
            img_array = np.array(img.convert("RGB"))
            
            # Gamma correction for dark images
            gamma = 2.5
            inv_gamma = 1.0 / gamma
            table = np.array([
                ((i / 255.0) ** inv_gamma) * 255
                for i in np.arange(0, 256)
            ]).astype("uint8")
            
            brightened = cv2.LUT(img_array, table)
            
            # CLAHE
            lab = cv2.cvtColor(brightened, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            merged = cv2.merge((cl, a, b))
            result = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
            
            return Image.fromarray(result)
            
        except Exception as e:
            logger.error(f"Night to day error: {e}")
            return img
