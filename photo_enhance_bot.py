#!/usr/bin/env python3
"""
Telegram Photo Enhancement Bot
Developer: Your Name
"""

import os
import io
import logging
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ============================================
# CONFIGURATION
# ============================================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Apna token yahan dalo
MAX_FILE_SIZE = 10 * 1024 * 1024   # 10 MB max

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# User ka photo store karne ke liye
user_photos = {}

# ============================================
# IMAGE PROCESSING FUNCTIONS
# ============================================

def enhance_brightness(img: Image.Image, factor: float = 1.5) -> Image.Image:
    """Image brightness badhao"""
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)

def enhance_contrast(img: Image.Image, factor: float = 1.5) -> Image.Image:
    """Image contrast badhao"""
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor)

def enhance_sharpness(img: Image.Image, factor: float = 2.0) -> Image.Image:
    """Image sharpness badhao"""
    enhancer = ImageEnhance.Sharpness(img)
    return enhancer.enhance(factor)

def enhance_color(img: Image.Image, factor: float = 1.5) -> Image.Image:
    """Image color saturation badhao"""
    enhancer = ImageEnhance.Color(img)
    return enhancer.enhance(factor)

def auto_enhance(img: Image.Image) -> Image.Image:
    """Automatic best enhancement"""
    # Brightness
    img = ImageEnhance.Brightness(img).enhance(1.2)
    # Contrast
    img = ImageEnhance.Contrast(img).enhance(1.3)
    # Sharpness
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    # Color
    img = ImageEnhance.Color(img).enhance(1.2)
    return img

def apply_grayscale(img: Image.Image) -> Image.Image:
    """Black & White filter"""
    return ImageOps.grayscale(img).convert("RGB")

def apply_sepia(img: Image.Image) -> Image.Image:
    """Sepia/vintage filter"""
    img_array = np.array(img.convert("RGB"))
    
    r = img_array[:,:,0]
    g = img_array[:,:,1]
    b = img_array[:,:,2]
    
    new_r = np.clip(r * 0.393 + g * 0.769 + b * 0.189, 0, 255)
    new_g = np.clip(r * 0.349 + g * 0.686 + b * 0.168, 0, 255)
    new_b = np.clip(r * 0.272 + g * 0.534 + b * 0.131, 0, 255)
    
    sepia_array = np.stack([new_r, new_g, new_b], axis=2).astype(np.uint8)
    return Image.fromarray(sepia_array)

def apply_blur(img: Image.Image) -> Image.Image:
    """Blur filter"""
    return img.filter(ImageFilter.GaussianBlur(radius=2))

def apply_sharpen(img: Image.Image) -> Image.Image:
    """Strong sharpen filter"""
    return img.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)

def apply_emboss(img: Image.Image) -> Image.Image:
    """Emboss effect"""
    return img.filter(ImageFilter.EMBOSS).convert("RGB")

def apply_edge_enhance(img: Image.Image) -> Image.Image:
    """Edge enhance filter"""
    return img.filter(ImageFilter.EDGE_ENHANCE_MORE)

def apply_cool_filter(img: Image.Image) -> Image.Image:
    """Cool/blue tint filter"""
    img_array = np.array(img.convert("RGB"))
    img_array[:,:,0] = np.clip(img_array[:,:,0] * 0.8, 0, 255)  # Red kam karo
    img_array[:,:,2] = np.clip(img_array[:,:,2] * 1.2, 0, 255)  # Blue badhao
    return Image.fromarray(img_array.astype(np.uint8))

def apply_warm_filter(img: Image.Image) -> Image.Image:
    """Warm/orange tint filter"""
    img_array = np.array(img.convert("RGB"))
    img_array[:,:,0] = np.clip(img_array[:,:,0] * 1.2, 0, 255)  # Red badhao
    img_array[:,:,2] = np.clip(img_array[:,:,2] * 0.8, 0, 255)  # Blue kam karo
    return Image.fromarray(img_array.astype(np.uint8))

def flip_horizontal(img: Image.Image) -> Image.Image:
    """Horizontal flip"""
    return img.transpose(Image.FLIP_LEFT_RIGHT)

def flip_vertical(img: Image.Image) -> Image.Image:
    """Vertical flip"""
    return img.transpose(Image.FLIP_TOP_BOTTOM)

def rotate_90(img: Image.Image) -> Image.Image:
    """90 degree rotate"""
    return img.rotate(90, expand=True)

def remove_noise(img: Image.Image) -> Image.Image:
    """Noise remove karo"""
    return img.filter(ImageFilter.MedianFilter(size=3))

def hd_upscale(img: Image.Image) -> Image.Image:
    """Image ko 2x upscale karo (HD effect)"""
    width, height = img.size
    new_size = (width * 2, height * 2)
    return img.resize(new_size, Image.LANCZOS)

# ============================================
# PIL Image ko bytes mein convert karo
# ============================================
def image_to_bytes(img: Image.Image) -> io.BytesIO:
    """PIL Image ko BytesIO mein convert karo"""
    output = io.BytesIO()
    
    # RGB ensure karo
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img.save(output, format='JPEG', quality=95)
    output.seek(0)
    return output

# ============================================
# KEYBOARD MENUS
# ============================================
def get_main_menu():
    """Main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("✨ Auto Enhance", callback_data="auto"),
            InlineKeyboardButton("🔆 Brightness", callback_data="brightness"),
        ],
        [
            InlineKeyboardButton("🎨 Contrast", callback_data="contrast"),
            InlineKeyboardButton("🔍 Sharpen", callback_data="sharpen"),
        ],
        [
            InlineKeyboardButton("🎭 Filters", callback_data="filters_menu"),
            InlineKeyboardButton("🔄 Rotate/Flip", callback_data="rotate_menu"),
        ],
        [
            InlineKeyboardButton("🎨 Color Boost", callback_data="color"),
            InlineKeyboardButton("📐 HD Upscale", callback_data="hd_upscale"),
        ],
        [
            InlineKeyboardButton("🔇 Remove Noise", callback_data="remove_noise"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_filters_menu():
    """Filters submenu"""
    keyboard = [
        [
            InlineKeyboardButton("⚫ Grayscale", callback_data="filter_grayscale"),
            InlineKeyboardButton("🟤 Sepia", callback_data="filter_sepia"),
        ],
        [
            InlineKeyboardButton("💙 Cool", callback_data="filter_cool"),
            InlineKeyboardButton("🔴 Warm", callback_data="filter_warm"),
        ],
        [
            InlineKeyboardButton("🌫️ Blur", callback_data="filter_blur"),
            InlineKeyboardButton("✏️ Emboss", callback_data="filter_emboss"),
        ],
        [
            InlineKeyboardButton("🔲 Edge Enhance", callback_data="filter_edge"),
            InlineKeyboardButton("↩️ Back", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_rotate_menu():
    """Rotate/Flip submenu"""
    keyboard = [
        [
            InlineKeyboardButton("↩️ Rotate 90°", callback_data="rotate_90"),
            InlineKeyboardButton("↔️ Flip H", callback_data="flip_h"),
        ],
        [
            InlineKeyboardButton("↕️ Flip V", callback_data="flip_v"),
            InlineKeyboardButton("↩️ Back", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================
# COMMAND HANDLERS
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user
    
    welcome_text = f"""
🤖 **Photo Enhance Bot mein aapka swagat hai!**

Namaste {user.first_name}! 👋

📸 **Kaise use karein:**
1. Koi bhi photo send karo
2. Enhancement option choose karo
3. Enhanced photo receive karo!

🛠️ **Available Features:**
• ✨ Auto Enhancement
• 🔆 Brightness/Contrast/Sharpness
• 🎨 Multiple Filters (Sepia, Cool, Warm, etc.)
• 🔄 Rotate & Flip
• 📐 HD Upscale (2x)
• 🔇 Noise Removal
• 🎨 Color Boost

💡 **Tip:** /help se sari commands dekho

Abhi ek photo bhejo! 📷
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
📖 **Bot Commands:**

/start - Bot start karo
/help - Yeh help message
/cancel - Current operation cancel karo

📸 **Photo Enhance Karne Ka Tarika:**
1. Bot ko photo bhejo
2. Enhancement menu aayega
3. Apna option choose karo
4. Enhanced photo milegi!

🎨 **Available Enhancements:**

**Basic:**
• ✨ Auto Enhance - Best automatic enhancement
• 🔆 Brightness - Photo roshan karo
• 🎨 Contrast - Contrast badhao
• 🔍 Sharpen - Sharp karo
• 🎨 Color Boost - Colors vibrant karo

**Filters:**
• ⚫ Grayscale - Black & White
• 🟤 Sepia - Vintage look
• 💙 Cool - Blue tint
• 🔴 Warm - Warm/orange tint
• 🌫️ Blur - Smooth blur
• ✏️ Emboss - 3D effect
• 🔲 Edge Enhance - Edges highlight

**Transforms:**
• ↩️ Rotate 90° - Rotate karo
• ↔️ Flip Horizontal - Mirror effect
• ↕️ Flip Vertical - Upside down
• 📐 HD Upscale - 2x bada karo
• 🔇 Remove Noise - Noise hatao

⚠️ **File Size:** Maximum 10MB
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown'
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel command"""
    user_id = update.effective_user.id
    
    if user_id in user_photos:
        del user_photos[user_id]
    
    await update.message.reply_text(
        "❌ Operation cancel ho gaya!\n\nNaya photo bhejo enhance karne ke liye. 📷"
    )

# ============================================
# PHOTO HANDLER
# ============================================

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Photo receive karne par handle karo"""
    user = update.effective_user
    user_id = user.id
    
    try:
        # Photo download karo
        await update.message.reply_text("⏳ Photo receive ho rahi hai...")
        
        # Sabse badi photo lo (best quality)
        photo = update.message.photo[-1]
        
        # Size check karo
        if photo.file_size and photo.file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                "❌ File bohot badi hai! Maximum 10MB allowed hai."
            )
            return
        
        # File download karo
        file = await photo.get_file()
        file_bytes = await file.download_as_bytearray()
        
        # PIL Image mein convert karo
        img = Image.open(io.BytesIO(file_bytes))
        
        # User ke liye save karo
        user_photos[user_id] = img.copy()
        
        # Image info
        width, height = img.size
        mode = img.mode
        
        info_text = f"""
✅ **Photo Receive Ho Gayi!**

📊 **Image Info:**
• Size: {width} x {height} pixels
• Mode: {mode}
• File Size: {photo.file_size // 1024 if photo.file_size else 'N/A'} KB

🎨 **Ab kya karna chahte ho?**
Neeche se option choose karo:
        """
        
        await update.message.reply_text(
            info_text,
            parse_mode='Markdown',
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        logger.error(f"Photo handler error: {e}")
        await update.message.reply_text(
            f"❌ Error aaya photo process karte waqt!\n\nError: {str(e)}"
        )

# ============================================
# CALLBACK QUERY HANDLER
# ============================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Button clicks handle karo"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # User ka photo check karo
    if user_id not in user_photos:
        await query.edit_message_text(
            "❌ Koi photo nahi mili!\n\nPehle ek photo bhejo. 📷"
        )
        return
    
    # Menu navigation
    if data == "back_main":
        await query.edit_message_text(
            "🎨 Enhancement choose karo:",
            reply_markup=get_main_menu()
        )
        return
    
    if data == "filters_menu":
        await query.edit_message_text(
            "🎨 Filter choose karo:",
            reply_markup=get_filters_menu()
        )
        return
    
    if data == "rotate_menu":
        await query.edit_message_text(
            "🔄 Transform choose karo:",
            reply_markup=get_rotate_menu()
        )
        return
    
    if data == "cancel":
        if user_id in user_photos:
            del user_photos[user_id]
        await query.edit_message_text(
            "❌ Cancel ho gaya!\n\nNaya photo bhejo. 📷"
        )
        return
    
    # Processing message
    await query.edit_message_text("⚙️ Processing... Please wait...")
    
    try:
        # Original image lo
        original_img = user_photos[user_id]
        enhanced_img = None
        caption = ""
        
        # Enhancement apply karo
        if data == "auto":
            enhanced_img = auto_enhance(original_img)
            caption = "✨ Auto Enhanced Photo"
            
        elif data == "brightness":
            enhanced_img = enhance_brightness(original_img)
            caption = "🔆 Brightness Enhanced Photo"
            
        elif data == "contrast":
            enhanced_img = enhance_contrast(original_img)
            caption = "🎨 Contrast Enhanced Photo"
            
        elif data == "sharpen":
            enhanced_img = enhance_sharpness(original_img)
            caption = "🔍 Sharpened Photo"
            
        elif data == "color":
            enhanced_img = enhance_color(original_img)
            caption = "🎨 Color Boosted Photo"
            
        elif data == "hd_upscale":
            enhanced_img = hd_upscale(original_img)
            caption = "📐 HD Upscaled Photo (2x)"
            
        elif data == "remove_noise":
            enhanced_img = remove_noise(original_img)
            caption = "🔇 Noise Removed Photo"
            
        # Filters
        elif data == "filter_grayscale":
            enhanced_img = apply_grayscale(original_img)
            caption = "⚫ Grayscale Filter"
            
        elif data == "filter_sepia":
            enhanced_img = apply_sepia(original_img)
            caption = "🟤 Sepia Filter"
            
        elif data == "filter_cool":
            enhanced_img = apply_cool_filter(original_img)
            caption = "💙 Cool Filter"
            
        elif data == "filter_warm":
            enhanced_img = apply_warm_filter(original_img)
            caption = "🔴 Warm Filter"
            
        elif data == "filter_blur":
            enhanced_img = apply_blur(original_img)
            caption = "🌫️ Blur Filter"
            
        elif data == "filter_emboss":
            enhanced_img = apply_emboss(original_img)
            caption = "✏️ Emboss Filter"
            
        elif data == "filter_edge":
            enhanced_img = apply_edge_enhance(original_img)
            caption = "🔲 Edge Enhanced Filter"
            
        # Transforms
        elif data == "rotate_90":
            enhanced_img = rotate_90(original_img)
            caption = "↩️ Rotated 90°"
            
        elif data == "flip_h":
            enhanced_img = flip_horizontal(original_img)
            caption = "↔️ Flipped Horizontal"
            
        elif data == "flip_v":
            enhanced_img = flip_vertical(original_img)
            caption = "↕️ Flipped Vertical"
        
        # Photo send karo
        if enhanced_img:
            img_bytes = image_to_bytes(enhanced_img)
            
            # Enhanced photo send karo
            back_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 More Enhancements", callback_data="back_main"),
                    InlineKeyboardButton("✅ Done", callback_data="cancel"),
                ]
            ])
            
            await query.message.reply_photo(
                photo=img_bytes,
                caption=f"✅ {caption}\n\n📷 Enhanced by Photo Enhance Bot",
                reply_markup=back_keyboard
            )
            
            await query.delete_message()
            
        else:
            await query.edit_message_text(
                "❌ Kuch galat hua!\n\nDobara try karo.",
                reply_markup=get_main_menu()
            )
            
    except Exception as e:
        logger.error(f"Callback handler error: {e}")
        await query.edit_message_text(
            f"❌ Enhancement fail ho gaya!\n\nError: {str(e)}\n\nDobara try karo.",
        )

# ============================================
# TEXT MESSAGE HANDLER
# ============================================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Text messages handle karo"""
    await update.message.reply_text(
        "📷 Bhai, photo bhejo enhance karne ke liye!\n\n"
        "Text se kuch nahi hoga 😄\n\n"
        "/help - Commands dekhne ke liye"
    )

# ============================================
# ERROR HANDLER
# ============================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Errors handle karo"""
    logger.error(f"Update {update} caused error {context.error}")

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    """Bot start karo"""
    print("🤖 Photo Enhance Bot Starting...")
    print("=" * 40)
    
    # Application banao
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers add karo
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    
    # Photo handler
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    
    # Callback handler (button clicks)
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Text handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    print("✅ Bot Successfully Started!")
    print("📱 Telegram pe ja aur photo bhejo!")
    print("=" * 40)
    print("❌ Band karne ke liye Ctrl+C dabao")
    
    # Bot run karo
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
