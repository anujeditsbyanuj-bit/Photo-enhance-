import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import logging
import random

logger = logging.getLogger(__name__)

class PhotoFilters:
    """All Photo Filters Collection"""
    
    # ==================
    # ARTISTIC FILTERS
    # ==================
    
    @staticmethod
    def pencil_sketch(img: Image.Image, color: bool = False) -> Image.Image:
        """Professional Pencil Sketch Effect"""
        try:
            img_array = np.array(img.convert("RGB"))
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            if color:
                # Color pencil sketch
                gray, color_sketch = cv2.pencilSketch(
                    img_bgr,
                    sigma_s=60, sigma_r=0.07, shade_factor=0.05
                )
                result = cv2.cvtColor(color_sketch, cv2.COLOR_BGR2RGB)
            else:
                # Black & White sketch
                gray_sketch, _ = cv2.pencilSketch(
                    img_bgr,
                    sigma_s=60, sigma_r=0.07, shade_factor=0.05
                )
                result = cv2.cvtColor(gray_sketch, cv2.COLOR_GRAY2RGB)
            
            return Image.fromarray(result)
            
        except Exception as e:
            logger.error(f"Pencil sketch error: {e}")
            # Fallback
            gray = img.convert("L")
            inverted = ImageOps_invert(gray)
            blurred = inverted.filter(ImageFilter.GaussianBlur(21))
            sketch = ImageChops_dodge(gray, blurred)
            return sketch.convert("RGB")
    
    @staticmethod
    def cartoon_effect(img: Image.Image) -> Image.Image:
        """Cartoon/Comic Effect"""
        try:
            img_array = np.array(img.convert("RGB"))
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Stylization
            cartoon = cv2.stylization(img_bgr, sigma_s=150, sigma_r=0.45)
            result = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
            
            return Image.fromarray(result)
            
        except Exception as e:
            logger.error(f"Cartoon error: {e}")
            return img
    
    @staticmethod
    def oil_painting(img: Image.Image) -> Image.Image:
        """Oil Painting Effect"""
        try:
            img_array = np.array(img.convert("RGB"))
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Detail enhance for oil painting look
            oil = cv2.detailEnhance(img_bgr, sigma_s=10, sigma_r=0.15)
            oil = cv2.stylization(oil, sigma_s=60, sigma_r=0.6)
            
            result = cv2.cvtColor(oil, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
            
        except Exception as e:
            logger.error(f"Oil painting error: {e}")
            return img
    
    @staticmethod
    def watercolor(img: Image.Image) -> Image.Image:
        """Watercolor Effect"""
        try:
            img_array = np.array(img.convert("RGB"))
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            watercolor = cv2.stylization(img_bgr, sigma_s=60, sigma_r=0.45)
            
            result = Image.fromarray(
                cv2.cvtColor(watercolor, cv2.COLOR_BGR2RGB)
            )
            result = ImageEnhance.Color(result).enhance(1.3)
            
            return result
            
        except Exception as e:
            logger.error(f"Watercolor error: {e}")
            return img
    
    @staticmethod
    def glitch_effect(img: Image.Image) -> Image.Image:
        """Cyberpunk Glitch Effect"""
        try:
            img_array = np.array(img.convert("RGB"))
            result = img_array.copy()
            
            h, w = img_array.shape[:2]
            
            # Random horizontal glitch lines
            num_glitches = random.randint(8, 15)
            for _ in range(num_glitches):
                y = random.randint(0, h - 1)
                glitch_height = random.randint(2, 20)
                shift = random.randint(-30, 30)
                
                y_end = min(y + glitch_height, h)
                
                # Shift RGB channels differently
                result[y:y_end, :, 0] = np.roll(
                    img_array[y:y_end, :, 0], shift, axis=1
                )
                result[y:y_end, :, 2] = np.roll(
                    img_array[y:y_end, :, 2], -shift, axis=1
                )
            
            # Color channel split
            result[:, :, 0] = np.roll(result[:, :, 0], 3, axis=1)
            result[:, :, 2] = np.roll(result[:, :, 2], -3, axis=1)
            
            # Scanlines
            for y in range(0, h, 4):
                result[y:y+1, :] = result[y:y+1, :] * 0.7
            
            return Image.fromarray(result.astype(np.uint8))
            
        except Exception as e:
            logger.error(f"Glitch error: {e}")
            return img
    
    @staticmethod
    def neon_glow(img: Image.Image) -> Image.Image:
        """Neon Glow Effect"""
        try:
            img_array = np.array(img.convert("RGB"))
            
            # Edge detection
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Dilate edges
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=2)
            
            # Colorize edges (neon cyan)
            neon = np.zeros_like(img_array)
            neon[:, :, 0] = edges * 0     # R
            neon[:, :, 1] = edges * 1     # G
            neon[:, :, 2] = edges * 1     # B
            
            # Blur for glow
            neon_blur = cv2.GaussianBlur(neon, (15, 15), 0)
            
            # Dark background
            dark = (img_array * 0.3).astype(np.uint8)
            
            # Combine
            result = cv2.add(dark, neon_blur)
            result = np.clip(result, 0, 255)
            
            return Image.fromarray(result.astype(np.uint8))
            
        except Exception as e:
            logger.error(f"Neon error: {e}")
            return img
    
    @staticmethod
    def vintage_film(img: Image.Image) -> Image.Image:
        """Vintage Film/Retro Effect"""
        try:
            img_array = np.array(img.convert("RGB")).astype(np.float32)
            
            # Fade colors
            img_array = img_array * 0.8 + 30
            
            # Sepia tone
            r = img_array[:,:,0] * 0.393 + img_array[:,:,1] * 0.769 + img_array[:,:,2] * 0.189
            g = img_array[:,:,0] * 0.349 + img_array[:,:,1] * 0.686 + img_array[:,:,2] * 0.168
            b = img_array[:,:,0] * 0.272 + img_array[:,:,1] * 0.534 + img_array[:,:,2] * 0.131
            
            img_array[:,:,0] = r * 0.6 + img_array[:,:,0] * 0.4
            img_array[:,:,1] = g * 0.6 + img_array[:,:,1] * 0.4
            img_array[:,:,2] = b * 0.6 + img_array[:,:,2] * 0.4
            
            # Vignette
            h, w = img_array.shape[:2]
            Y, X = np.ogrid[:h, :w]
            cx, cy = w / 2, h / 2
            dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
            max_dist = np.sqrt(cx**2 + cy**2)
            vignette = 1 - (dist / max_dist) * 0.5
            
            for c in range(3):
                img_array[:,:,c] *= vignette
            
            # Film grain
            grain = np.random.normal(0, 8, img_array.shape).astype(np.float32)
            img_array += grain
            
            result = np.clip(img_array, 0, 255).astype(np.uint8)
            return Image.fromarray(result)
            
        except Exception as e:
            logger.error(f"Vintage error: {e}")
            return img
    
    @staticmethod
    def cyberpunk(img: Image.Image) -> Image.Image:
        """Cyberpunk/Futuristic Effect"""
        try:
            img_array = np.array(img.convert("RGB")).astype(np.float32)
            
            # Boost cyan and magenta
            img_array[:,:,0] = np.clip(img_array[:,:,0] * 0.7, 0, 255)  # R down
            img_array[:,:,1] = np.clip(img_array[:,:,1] * 1.3, 0, 255)  # G up
            img_array[:,:,2] = np.clip(img_array[:,:,2] * 1.4, 0, 255)  # B up
            
            # High contrast
            result = Image.fromarray(img_array.astype(np.uint8))
            result = ImageEnhance.Contrast(result).enhance(1.5)
            result = ImageEnhance.Color(result).enhance(1.8)
            
            return result
            
        except Exception as e:
            logger.error(f"Cyberpunk error: {e}")
            return img
    
    @staticmethod
    def pop_art(img: Image.Image) -> Image.Image:
        """Andy Warhol Pop Art Effect"""
        try:
            img_array = np.array(img.convert("RGB"))
            
            # Posterize (reduce colors)
            result = Image.fromarray(img_array)
            result = ImageOps_posterize(result, 3)
            
            # High saturation
            result = ImageEnhance.Color(result).enhance(3.0)
            result = ImageEnhance.Contrast(result).enhance(1.5)
            
            return result
            
        except Exception as e:
            logger.error(f"Pop art error: {e}")
            return img
    
    @staticmethod
    def infrared(img: Image.Image) -> Image.Image:
        """Infrared Photo Effect"""
        try:
            img_array = np.array(img.convert("RGB"))
            
            # Swap channels
            r = img_array[:,:,0].copy()
            g = img_array[:,:,1].copy()
            b = img_array[:,:,2].copy()
            
            # Infrared: highlights greens, inverts darks
            img_array[:,:,0] = np.clip(255 - b, 0, 255)
            img_array[:,:,1] = np.clip(g * 1.5, 0, 255)
            img_array[:,:,2] = np.clip(255 - r, 0, 255)
            
            result = Image.fromarray(img_array.astype(np.uint8))
            result = ImageEnhance.Contrast(result).enhance(1.3)
            
            return result
            
        except Exception as e:
            logger.error(f"Infrared error: {e}")
            return img
    
    @staticmethod
    def pixelate(img: Image.Image, pixel_size: int = 10) -> Image.Image:
        """Pixel Art Effect"""
        try:
            w, h = img.size
            small = img.resize(
                (w // pixel_size, h // pixel_size),
                Image.NEAREST
            )
            pixelated = small.resize((w, h), Image.NEAREST)
            return pixelated
            
        except Exception as e:
            logger.error(f"Pixelate error: {e}")
            return img
    
    @staticmethod
    def mirror_effect(img: Image.Image) -> Image.Image:
        """4-way Mirror Effect"""
        try:
            w, h = img.size
            half_w, half_h = w // 2, h // 2
            
            # Top-left quadrant
            top_left = img.crop((0, 0, half_w, half_h))
            
            # Mirror versions
            top_right = top_left.transpose(Image.FLIP_LEFT_RIGHT)
            bottom_left = top_left.transpose(Image.FLIP_TOP_BOTTOM)
            bottom_right = top_left.transpose(Image.FLIP_LEFT_RIGHT).transpose(
                Image.FLIP_TOP_BOTTOM
            )
            
            # Combine
            result = Image.new("RGB", (w, h))
            result.paste(top_left, (0, 0))
            result.paste(top_right, (half_w, 0))
            result.paste(bottom_left, (0, half_h))
            result.paste(bottom_right, (half_w, half_h))
            
            return result
            
        except Exception as e:
            logger.error(f"Mirror error: {e}")
            return img
    
    @staticmethod
    def duotone(
        img: Image.Image,
        color1: tuple = (0, 0, 128),
        color2: tuple = (255, 200, 0)
    ) -> Image.Image:
        """Duotone/Two-Color Effect"""
        try:
            gray = np.array(img.convert("L"))
            
            # Map grayscale to two colors
            r = np.interp(gray, [0, 255], [color1[0], color2[0]])
            g = np.interp(gray, [0, 255], [color1[1], color2[1]])
            b = np.interp(gray, [0, 255], [color1[2], color2[2]])
            
            result = np.stack([r, g, b], axis=2).astype(np.uint8)
            return Image.fromarray(result)
            
        except Exception as e:
            logger.error(f"Duotone error: {e}")
            return img
    
    @staticmethod
    def vignette(img: Image.Image, strength: float = 0.5) -> Image.Image:
        """Add vignette border effect"""
        try:
            img_array = np.array(img.convert("RGB")).astype(np.float32)
            h, w = img_array.shape[:2]
            
            Y, X = np.ogrid[:h, :w]
            cx, cy = w / 2, h / 2
            dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
            max_dist = np.sqrt(cx**2 + cy**2)
            vignette_mask = 1 - (dist / max_dist) * strength
            
            for c in range(3):
                img_array[:,:,c] *= vignette_mask
            
            return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
            
        except Exception as e:
            logger.error(f"Vignette error: {e}")
            return img


# Helper functions
def ImageOps_invert(img):
    from PIL import ImageOps
    return ImageOps.invert(img)

def ImageOps_posterize(img, bits):
    from PIL import ImageOps
    return ImageOps.posterize(img, bits)
