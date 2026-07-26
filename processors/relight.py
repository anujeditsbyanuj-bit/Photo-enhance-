import numpy as np
import cv2
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class AIRelight:
    """AI Relighting - Studio Quality Lighting Effects"""
    
    @staticmethod
    def studio_light(img: Image.Image) -> Image.Image:
        """Professional studio lighting effect"""
        try:
            img_array = np.array(img.convert("RGB")).astype(np.float32)
            h, w = img_array.shape[:2]
            
            # Create radial light from top-center
            Y, X = np.ogrid[:h, :w]
            cx, cy = w / 2, h * 0.1  # Light source: top center
            
            dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
            max_dist = np.sqrt(w**2 + h**2)
            
            # Light falloff
            light = 1.0 - (dist / max_dist) * 0.6
            light = np.clip(light, 0.4, 1.3)
            
            # Apply lighting
            for c in range(3):
                img_array[:,:,c] *= light
            
            result = np.clip(img_array, 0, 255).astype(np.uint8)
            
            # Enhance after lighting
            from PIL import ImageEnhance
            pil_result = Image.fromarray(result)
            pil_result = ImageEnhance.Contrast(pil_result).enhance(1.2)
            
            return pil_result
            
        except Exception as e:
            logger.error(f"Studio light error: {e}")
            return img
    
    @staticmethod
    def golden_hour(img: Image.Image) -> Image.Image:
        """Golden Hour / Sunset Lighting"""
        try:
            img_array = np.array(img.convert("RGB")).astype(np.float32)
            h, w = img_array.shape[:2]
            
            # Gradient from right (sunset side)
            X = np.linspace(0.7, 1.3, w)
            gradient = np.tile(X, (h, 1))
            
            # Warm tones
            img_array[:,:,0] = np.clip(img_array[:,:,0] * gradient * 1.2, 0, 255)  # R+
            img_array[:,:,1] = np.clip(img_array[:,:,1] * gradient * 0.9, 0, 255)  # G~
            img_array[:,:,2] = np.clip(img_array[:,:,2] * 0.7, 0, 255)              # B-
            
            result = np.clip(img_array, 0, 255).astype(np.uint8)
            
            from PIL import ImageEnhance
            pil = Image.fromarray(result)
            pil = ImageEnhance.Color(pil).enhance(1.4)
            
            return pil
            
        except Exception as e:
            logger.error(f"Golden hour error: {e}")
            return img
    
    @staticmethod
    def dramatic_light(img: Image.Image) -> Image.Image:
        """Dramatic Side Lighting (Rembrandt style)"""
        try:
            img_array = np.array(img.convert("RGB")).astype(np.float32)
            h, w = img_array.shape[:2]
            
            # Light from left side
            X = np.linspace(1.4, 0.3, w)
            Y = np.linspace(1.2, 0.8, h)
            
            h_gradient = np.tile(X, (h, 1))
            v_gradient = np.tile(Y.reshape(-1, 1), (1, w))
            
            combined = (h_gradient * v_gradient)
            combined = np.clip(combined, 0.2, 1.5)
            
            for c in range(3):
                img_array[:,:,c] *= combined
            
            result = np.clip(img_array, 0, 255).astype(np.uint8)
            
            from PIL import ImageEnhance
            pil = Image.fromarray(result)
            pil = ImageEnhance.Contrast(pil).enhance(1.4)
            
            return pil
            
        except Exception as e:
            logger.error(f"Dramatic light error: {e}")
            return img
    
    @staticmethod
    def soft_beauty(img: Image.Image) -> Image.Image:
        """Soft Beauty/Fashion Lighting"""
        try:
            img_array = np.array(img.convert("RGB"))
            
            # Bilateral filter for soft skin
            soft = cv2.bilateralFilter(img_array, 15, 75, 75)
            
            # Slight brightness boost
            soft = np.clip(soft.astype(np.float32) * 1.15, 0, 255).astype(np.uint8)
            
            # Top-center fill light
            h, w = soft.shape[:2]
            Y, X = np.ogrid[:h, :w]
            cx, cy = w / 2, 0
            dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
            max_dist = np.sqrt(w**2 + h**2)
            fill = 1.0 + (1 - dist / max_dist) * 0.2
            
            result = soft.astype(np.float32)
            for c in range(3):
                result[:,:,c] *= fill
            
            pil = Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))
            
            from PIL import ImageEnhance
            pil = ImageEnhance.Color(pil).enhance(1.1)
            
            return pil
            
        except Exception as e:
            logger.error(f"Soft beauty error: {e}")
            return img
    
    @staticmethod
    def neon_light(img: Image.Image) -> Image.Image:
        """Neon/Club Lighting Effect"""
        try:
            img_array = np.array(img.convert("RGB")).astype(np.float32)
            
            # Purple/magenta tint from top
            img_array[:,:,0] = np.clip(img_array[:,:,0] * 1.3, 0, 255)  # R+
            img_array[:,:,1] = np.clip(img_array[:,:,1] * 0.5, 0, 255)  # G-
            img_array[:,:,2] = np.clip(img_array[:,:,2] * 1.4, 0, 255)  # B+
            
            result = np.clip(img_array, 0, 255).astype(np.uint8)
            
            from PIL import ImageEnhance
            pil = Image.fromarray(result)
            pil = ImageEnhance.Contrast(pil).enhance(1.3)
            pil = ImageEnhance.Color(pil).enhance(1.5)
            
            return pil
            
        except Exception as e:
            logger.error(f"Neon light error: {e}")
            return img
