#!/usr/bin/env python3
"""
🤖 AI Photo & Video Enhancement Bot
Complete Professional Version
"""

import os
import io
import logging
import asyncio
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from PIL import Image

# Import our modules
from config import BOT_TOKEN, MAX_PHOTO_SIZE, MAX_VIDEO_SIZE, TEMP_DIR
from processors.enhancer import AIEnhancer
from processors.bg_remover import BackgroundRemover
from processors.filters import PhotoFilters
from processors.relight import AIRelight
from processors.video_processor import VideoProcessor
from utils.keyboards import (
    main_menu, filters_menu, relight_menu,
    video_menu, after_enhance_menu
)

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Temp directory
Path(TEMP_DIR).mkdir(exist_ok=True)

# User data store
user_data = {}

# ============================================
# HELPER FUNCTIONS
# ============================================

def pil_to_bytes(img: Image.Image, fmt: str = "JPEG") -> io.BytesIO:
    """PIL Image to BytesIO"""
    output = io.BytesIO()
    if fmt == "PNG":
        img.save(output, format="PNG", optimize=True)
    else:
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(output, format="JPEG", quality=95)
    output.seek(0)
    return output

def get_file_size_mb(size_bytes: int) -> str:
    return f"{size_bytes / (1024*1024):.1f} MB"

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"""
🤖 *AI Photo & Video Enhancement Bot*

Namaste {user.first_name}! 👋

*🚀 Kya kar sakta hai yeh bot:*

📸 *Photo Features:*
• ✨ AI Auto Enhancement
• 📐 AI Upscale (2x / 4x HD)
• 🎨 Background Remove → Transparent PNG
• 🔵 Background Blur (DSLR effect)
• 💡 AI Relight (5 studio effects)
• 👤 Portrait & Skin Enhancement
• 🌄 HDR Effect
• 🌙 Night → Day Conversion

🎨 *Filters (14+):*
• ✏️ Pencil Sketch (B&W / Color)
• 🎭 Cartoon & Oil Painting
• 💧 Watercolor
• ⚡ Glitch & Neon Glow
• 📽️ Vintage Film
• 🤖 Cyberpunk
• 🎭 Duotone & Pop Art
• 📷 Infrared & Mirror

🎬 *Video Features:*
• ✨ AI Frame-by-Frame Enhancement
• 🔇 Video Denoise
• 🌄 HDR Video
• 🔍 Video Sharpen
• Max Size: 50 MB

*📖 Commands:*
/start - Bot start karo
/help - Help dekho
/cancel - Cancel karo

*Abhi ek photo ya video bhejo!* 📷
    """
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📖 *Help Guide*

*Photo bhejne ka tarika:*
1. Bot ko photo bhejo
2. Enhancement menu aayega
3. Apna option choose karo
4. Enhanced photo milegi!

*Video bhejne ka tarika:*
1. Video file bhejo (max 50MB)
2. Enhancement type choose karo
3. Wait karo (thoda time lagega)
4. Enhanced video milegi!

*Tips:*
• Background remove ke liye clear photo bhejo
• Portrait enhance ke liye face clearly visible hona chahiye
• Video enhance mein 1-3 minutes lag sakte hain
• /cancel se koi bhi operation band karo

*Supported Formats:*
📸 Photos: JPG, PNG, WEBP
🎬 Videos: MP4, AVI, MOV, MKV
    """
    await update.message.reply_text(text, parse_mode="Markdown")

async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_data:
        del user_data[uid]
    await update.message.reply_text(
        "❌ Cancel ho gaya!\n\nNaya photo ya video bhejo. 📷"
    )

# ============================================
# PHOTO HANDLER
# ============================================

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    try:
        msg = await update.message.reply_text("📥 Photo receive ho rahi hai...")
        
        photo = update.message.photo[-1]
        
        if photo.file_size and photo.file_size > MAX_PHOTO_SIZE:
            await msg.edit_text(
                f"❌ File bohot badi hai!\n"
                f"Max allowed: {get_file_size_mb(MAX_PHOTO_SIZE)}\n"
                f"Aapki file: {get_file_size_mb(photo.file_size)}"
            )
            return
        
        file = await photo.get_file()
        file_bytes = await file.download_as_bytearray()
        
        img = Image.open(io.BytesIO(file_bytes))
        user_data[uid] = {
            "type": "photo",
            "image": img.copy(),
            "original": img.copy()
        }
        
        w, h = img.size
        size_kb = len(file_bytes) // 1024
        
        info = (
            f"✅ *Photo Ready!*\n\n"
            f"📊 *Info:*\n"
            f"• Resolution: `{w} × {h}` px\n"
            f"• Size: `{size_kb} KB`\n"
            f"• Mode: `{img.mode}`\n\n"
            f"🎨 *Enhancement choose karo:*"
        )
        
        await msg.edit_text(info, parse_mode="Markdown", reply_markup=main_menu())
        
    except Exception as e:
        logger.error(f"Photo handler error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ============================================
# VIDEO HANDLER
# ============================================

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    try:
        video = update.message.video or update.message.document
        
        if not video:
            return
        
        # Size check
        if video.file_size and video.file_size > MAX_VIDEO_SIZE:
            await update.message.reply_text(
                f"❌ Video bohot badi hai!\n"
                f"Max: {get_file_size_mb(MAX_VIDEO_SIZE)}\n"
                f"Aapki: {get_file_size_mb(video.file_size)}"
            )
            return
        
        msg = await update.message.reply_text(
            "📥 Video download ho rahi hai... (thoda wait karo)"
        )
        
        file = await video.get_file()
        input_path = os.path.join(TEMP_DIR, f"{uid}_input.mp4")
        await file.download_to_drive(input_path)
        
        # Get video info
        info = VideoProcessor.get_video_info(input_path)
        
        user_data[uid] = {
            "type": "video",
            "input_path": input_path,
        }
        
        duration = info.get('duration', 0)
        width = info.get('width', 0)
        height = info.get('height', 0)
        fps = info.get('fps', 0)
        
        text = (
            f"✅ *Video Ready!*\n\n"
            f"📊 *Info:*\n"
            f"• Resolution: `{width} × {height}`\n"
            f"• FPS: `{fps}`\n"
            f"• Duration: `{duration}s`\n"
            f"• Size: `{get_file_size_mb(video.file_size)}`\n\n"
            f"🎬 *Enhancement choose karo:*\n"
            f"_(Note: Processing mein 1-3 min lag sakte hain)_"
        )
        
        await msg.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=video_menu()
        )
        
    except Exception as e:
        logger.error(f"Video handler error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ============================================
# CALLBACK HANDLER
# ============================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    uid = query.from_user.id
    data = query.data
    
    # Navigation
    if data == "back_main":
        await query.edit_message_text(
            "🎨 Enhancement choose karo:",
            reply_markup=main_menu()
        )
        return
    
    if data == "filters_menu":
        await query.edit_message_text(
            "🎨 Filter choose karo:",
            reply_markup=filters_menu()
        )
        return
    
    if data == "relight_menu":
        await query.edit_message_text(
            "💡 Lighting effect choose karo:",
            reply_markup=relight_menu()
        )
        return
    
    if data in ("cancel", "done"):
        if uid in user_data:
            # Cleanup video files
            if user_data[uid].get("type") == "video":
                for key in ["input_path", "output_path"]:
                    path = user_data[uid].get(key)
                    if path and os.path.exists(path):
                        os.remove(path)
            del user_data[uid]
        await query.edit_message_text("✅ Done! Naya photo ya video bhejo. 📷")
        return
    
    # Check user data
    if uid not in user_data:
        await query.edit_message_text(
            "❌ Koi photo/video nahi mili!\nPehle kuch bhejo. 📷"
        )
        return
    
    utype = user_data[uid].get("type")
    
    # ==================
    # VIDEO PROCESSING
    # ==================
    if utype == "video" and data.startswith("v_"):
        await _process_video(query, uid, data)
        return
    
    # ==================
    # PHOTO PROCESSING
    # ==================
    if utype == "photo":
        await _process_photo(query, uid, data)

async def _process_video(query, uid: int, data: str):
    """Video processing"""
    try:
        v_type_map = {
            "v_auto": "auto",
            "v_denoise": "denoise",
            "v_hdr": "hdr",
            "v_sharpen": "sharpen",
        }
        
        enhancement = v_type_map.get(data, "auto")
        
        await query.edit_message_text(
            f"⚙️ *Video enhance ho rahi hai...*\n\n"
            f"Type: `{enhancement}`\n"
            f"⏳ Please wait (1-3 minutes)...\n\n"
            f"_Yeh bot frame-by-frame process karta hai_",
            parse_mode="Markdown"
        )
        
        input_path = user_data[uid]["input_path"]
        output_path = os.path.join(
            TEMP_DIR, f"{uid}_output_{enhancement}.mp4"
        )
        
        # Process in thread pool
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None,
            VideoProcessor.enhance_video,
            input_path, output_path, enhancement
        )
        
        if success and os.path.exists(output_path):
            await query.message.reply_video(
                video=open(output_path, "rb"),
                caption=(
                    f"✅ *Video Enhanced!*\n"
                    f"Type: {enhancement.title()}\n\n"
                    f"🤖 AI Video Enhancement Bot"
                ),
                parse_mode="Markdown"
            )
            await query.delete_message()
            
            # Cleanup
            for path in [input_path, output_path]:
                if os.path.exists(path):
                    os.remove(path)
        else:
            await query.edit_message_text(
                "❌ Video enhance fail ho gayi!\nDobara try karo."
            )
            
    except Exception as e:
        logger.error(f"Video process error: {e}")
        await query.edit_message_text(f"❌ Error: {str(e)}")

async def _process_photo(query, uid: int, data: str):
    """Photo processing"""
    
    # Processing map
    process_map = {
        # AI Enhancements
        "ai_auto":     ("✨ AI Auto Enhanced",        lambda i: AIEnhancer.auto_enhance(i)),
        "upscale_2x":  ("📐 AI Upscaled 2x",          lambda i: AIEnhancer.upscale_image(i, 2)),
        "upscale_4x":  ("📐 AI Upscaled 4x",          lambda i: AIEnhancer.upscale_image(i, 4)),
        "portrait":    ("👤 Portrait Enhanced",        lambda i: AIEnhancer.enhance_portrait(i)),
        "hdr":         ("🌄 HDR Effect",               lambda i: AIEnhancer.hdr_effect(i)),
        "night_day":   ("🌙 Night → Day",              lambda i: AIEnhancer.night_to_day(i)),
        
        # Background
        "remove_bg":   ("🎨 Background Removed",       lambda i: BackgroundRemover.remove_background_rembg(i), "PNG"),
        "blur_bg":     ("🔵 Background Blurred",       lambda i: BackgroundRemover.blur_background(i)),
        "bg_white":    ("⬜ White Background",          lambda i: BackgroundRemover.add_background_color(i, (255,255,255))),
        "bg_black":    ("⬛ Black Background",          lambda i: BackgroundRemover.add_background_color(i, (0,0,0))),
        
        # Relight
        "r_studio":    ("💡 Studio Light",             lambda i: AIRelight.studio_light(i)),
        "r_golden":    ("🌅 Golden Hour",              lambda i: AIRelight.golden_hour(i)),
        "r_dramatic":  ("🎭 Dramatic Light",           lambda i: AIRelight.dramatic_light(i)),
        "r_beauty":    ("✨ Soft Beauty",              lambda i: AIRelight.soft_beauty(i)),
        "r_neon":      ("🌈 Neon Light",               lambda i: AIRelight.neon_light(i)),
        
        # Filters
        "f_pencil":    ("✏️ Pencil Sketch",            lambda i: PhotoFilters.pencil_sketch(i)),
        "f_cartoon":   ("🎨 Cartoon",                  lambda i: PhotoFilters.cartoon_effect(i)),
        "f_oil":       ("🖌️ Oil Painting",             lambda i: PhotoFilters.oil_painting(i)),
        "f_watercolor":("💧 Watercolor",               lambda i: PhotoFilters.watercolor(i)),
        "f_glitch":    ("⚡ Glitch Effect",            lambda i: PhotoFilters.glitch_effect(i)),
        "f_neon":      ("🌈 Neon Glow",               lambda i: PhotoFilters.neon_glow(i)),
        "f_vintage":   ("📽️ Vintage Film",             lambda i: PhotoFilters.vintage_film(i)),
        "f_cyberpunk": ("🤖 Cyberpunk",               lambda i: PhotoFilters.cyberpunk(i)),
        "f_duotone":   ("🎭 Duotone",                  lambda i: PhotoFilters.duotone(i)),
        "f_popart":    ("🎨 Pop Art",                  lambda i: PhotoFilters.pop_art(i)),
        "f_infrared":  ("📷 Infrared",                 lambda i: PhotoFilters.infrared(i)),
        "f_mirror":    ("🪞 Mirror Effect",            lambda i: PhotoFilters.mirror_effect(i)),
        "f_sepia":     ("🟫 Sepia",                    lambda i: PhotoFilters.vintage_film(i)),
        "f_pixelate":  ("⬛ Pixelated",               lambda i: PhotoFilters.pixelate(i)),
        "f_vignette":  ("🌑 Vignette",                lambda i: PhotoFilters.vignette(i)),
    }
    
    if data not in process_map:
        await query.edit_message_text(
            "❓ Unknown option!\n",
            reply_markup=main_menu()
        )
        return
    
    info = process_map[data]
    caption_text = info[0]
    process_func = info[1]
    output_format = info[2] if len(info) > 2 else "JPEG"
    
    await query.edit_message_text(f"⚙️ Processing: {caption_text}...")
    
    try:
        original_img = user_data[uid]["original"]
        
        # Run in executor (non-blocking)
        loop = asyncio.get_event_loop()
        enhanced = await loop.run_in_executor(None, process_func, original_img)
        
        # Convert to bytes
        img_bytes = pil_to_bytes(enhanced, output_format)
        
        full_caption = (
            f"✅ *{caption_text}*\n\n"
            f"🤖 AI Photo Enhancement Bot"
        )
        
        if output_format == "PNG":
            await query.message.reply_document(
                document=img_bytes,
                filename="enhanced_transparent.png",
                caption=full_caption,
                parse_mode="Markdown",
                reply_markup=after_enhance_menu()
            )
        else:
            await query.message.reply_photo(
                photo=img_bytes,
                caption=full_caption,
                parse_mode="Markdown",
                reply_markup=after_enhance_menu()
            )
        
        await query.delete_message()
        
    except Exception as e:
        logger.error(f"Photo process error: {e}")
        await query.edit_message_text(
            f"❌ Processing fail!\nError: {str(e)}\n\nDobara try karo.",
            reply_markup=main_menu()
        )

# ============================================
# TEXT HANDLER
# ============================================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📷 Photo ya 🎬 Video bhejo enhance karne ke liye!\n\n"
        "/help - Help ke liye"
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# ============================================
# MAIN
# ============================================

def main():
    print("=" * 50)
    print("🤖 AI Photo & Video Enhancement Bot")
    print("=" * 50)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    
    # Media handlers
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(
        filters.VIDEO | (filters.Document.VIDEO), video_handler
    ))
    
    # Callback
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    # Error
    app.add_error_handler(error_handler)
    
    print("✅ Bot Started!")
    print("📱 Telegram pe jao aur photo/video bhejo!")
    print("❌ Band karne ke liye: Ctrl+C")
    print("=" * 50)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
