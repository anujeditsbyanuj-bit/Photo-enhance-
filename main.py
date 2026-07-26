#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║   🤖 AI Photo Enhancement Bot           ║
║   ✨ Enhance · 💡 Relight · 🔍 Upscale  ║
╚══════════════════════════════════════════╝
"""

import asyncio
import io
import logging
import os

from telegram import Update
from telegram.ext import (
    Application, CallbackQueryHandler,
    CommandHandler, ContextTypes,
    MessageHandler, filters,
)
from PIL import Image

from config       import BOT_TOKEN, MAX_SIZE, TEMP_DIR
from ai.enhancer  import Enhancer
from ai.upscaler  import Upscaler
from ai.relight   import Relight
from ui.keyboards import home, enhance_menu, relight_menu, result_menu
from utils.image_utils import load_image, to_bytes, img_info

# ── logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

os.makedirs(TEMP_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────
#  DISPATCH TABLE  (callback_data → (fn, label, fmt))
# ─────────────────────────────────────────────────────────────────────────
ENHANCE_MAP = {
    # Enhance
    "e_auto":     (Enhancer.auto,            "✨ Auto Enhanced",      "JPEG"),
    "e_restore":  (Enhancer.deep_restore,    "🖼️ Deep Restored",      "JPEG"),
    "e_portrait": (Enhancer.portrait_retouch,"👤 Portrait Retouched", "JPEG"),
    "e_hdr":      (Enhancer.hdr,             "🌄 HDR Look",           "JPEG"),
    "e_night":    (Enhancer.night_fix,       "🌙 Night Fixed",        "JPEG"),
    "e_vivid":    (Enhancer.vivid,           "🌈 Vivid Colours",      "JPEG"),
    "e_denoise":  (Enhancer.denoise_only,    "🔇 Denoised",           "JPEG"),
    "e_sharpen":  (Enhancer.sharpen_only,    "🔪 Sharpened",          "JPEG"),
    # Relight
    "r_studio":   (Relight.studio_white,     "🤍 Studio White",       "JPEG"),
    "r_golden":   (Relight.golden_hour,      "🌅 Golden Hour",        "JPEG"),
    "r_dramatic": (Relight.dramatic_shadow,  "🎭 Dramatic Shadow",    "JPEG"),
    "r_beauty":   (Relight.soft_beauty,      "💄 Soft Beauty",        "JPEG"),
    "r_neon":     (Relight.neon_night,       "🌈 Neon Night",         "JPEG"),
    "r_moon":     (Relight.moonlight,        "🌙 Moonlight",          "JPEG"),
    "r_candle":   (Relight.warm_candlelight, "🕯️ Candlelight",        "JPEG"),
    "r_forest":   (Relight.forest_green,     "🌿 Forest Green",       "JPEG"),
}

# ─────────────────────────────────────────────────────────────────────────
#  COMMANDS
# ─────────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Namaste *{name}*!\n\n"
        "🤖 *AI Photo Enhancement Bot* mein aapka swagat hai!\n\n"
        "*Kya kar sakta hoon:*\n"
        "• ✨ AI Auto Enhance\n"
        "• 🖼️ Deep Restore (purani photos)\n"
        "• 👤 Portrait Skin Retouch\n"
        "• 🌄 HDR Look\n"
        "• 🌙 Night Fix\n"
        "• 💡 8 Studio Relight Presets\n"
        "• 🔍 Upscale ×2 / ×4 (HD)\n"
        "• 📏 Enlarge to 12 MP (print ready)\n\n"
        "📷 *Bas ek photo bhejo — menu aa jaayega!*",
        parse_mode="Markdown",
    )

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 *Help*\n\n"
        "1️⃣  Photo bhejo\n"
        "2️⃣  Menu se option choose karo\n"
        "3️⃣  Enhanced photo milegi!\n\n"
        "*Limits:*  max `20 MB` per photo\n\n"
        "/start — restart\n"
        "/cancel — sab clear karo",
        parse_mode="Markdown",
    )

async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    ctx.user_data.clear()
    await update.message.reply_text("❌ Cancel ho gaya.  Photo bhejo 📷")

# ─────────────────────────────────────────────────────────────────────────
#  PHOTO HANDLER
# ─────────────────────────────────────────────────────────────────────────

async def on_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.message.photo[-1]          # best quality

    # size guard
    if photo.file_size and photo.file_size > MAX_SIZE:
        await update.message.reply_text(
            f"❌ Photo `{photo.file_size // (1024*1024):.1f} MB` hai — "
            f"max `{MAX_SIZE // (1024*1024)} MB` allowed.\n"
            "Chhoti photo bhejo.",
            parse_mode="Markdown",
        )
        return

    status = await update.message.reply_text("📥 Receiving photo…")

    raw   = await (await photo.get_file()).download_as_bytearray()
    img   = load_image(bytes(raw))

    ctx.user_data["img"] = img          # store PIL Image

    await status.edit_text(
        f"✅ *Photo ready!*\n\n{img_info(img)}\n\n"
        "⬇️ Enhancement choose karo:",
        parse_mode="Markdown",
        reply_markup=home(),
    )

# ─────────────────────────────────────────────────────────────────────────
#  CALLBACK HANDLER
# ─────────────────────────────────────────────────────────────────────────

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q    = update.callback_query
    data = q.data
    await q.answer()

    # ── navigation ───────────────────────────────────────────────────────
    if data == "home":
        await q.edit_message_text(
            "⬇️ Enhancement choose karo:",
            reply_markup=home(),
        )
        return

    if data == "m_enhance":
        await q.edit_message_text(
            "✨ *AI Enhancement* — option choose karo:",
            parse_mode="Markdown",
            reply_markup=enhance_menu(),
        )
        return

    if data == "m_relight":
        await q.edit_message_text(
            "💡 *AI Relight* — lighting preset choose karo:",
            parse_mode="Markdown",
            reply_markup=relight_menu(),
        )
        return

    if data == "cancel":
        ctx.user_data.clear()
        await q.edit_message_text("✅ Done!  Naya photo bhejo 📷")
        return

    # ── check image ──────────────────────────────────────────────────────
    img: Image.Image | None = ctx.user_data.get("img")
    if img is None:
        await q.edit_message_text("❌ Koi photo nahi mili.  Pehle photo bhejo 📷")
        return

    # ── upscale / enlarge ────────────────────────────────────────────────
    if data in ("up_2", "up_4", "enlarge"):
        factor = 2 if data == "up_2" else 4
        label  = (
            "🔍 Upscaled ×2" if data == "up_2" else
            "🔍 Upscaled ×4" if data == "up_4" else
            "📏 Enlarged → 12 MP"
        )
        await q.edit_message_text(f"⚙️ Processing: *{label}* …", parse_mode="Markdown")

        loop    = asyncio.get_event_loop()
        fn      = (lambda i: Upscaler.enlarge(i)) if data == "enlarge" else \
                  (lambda i: Upscaler.upscale(i, factor))
        result  = await loop.run_in_executor(None, fn, img)

        # update stored image so further ops work on result
        ctx.user_data["img"] = result

        w, h = result.size
        await q.message.reply_photo(
            photo   = to_bytes(result, "JPEG"),
            caption = (
                f"✅ *{label}*\n\n"
                f"📐 New size: `{w} × {h} px`\n\n"
                "🎨 Aur kuch karna hai?"
            ),
            parse_mode    = "Markdown",
            reply_markup  = result_menu(),
        )
        await q.delete_message()
        return

    # ── enhance / relight ────────────────────────────────────────────────
    if data in ENHANCE_MAP:
        fn, label, fmt = ENHANCE_MAP[data]

        await q.edit_message_text(
            f"⚙️ *{label}* apply ho raha hai…",
            parse_mode="Markdown",
        )

        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, fn, img)

        ctx.user_data["img"] = result          # chain edits

        buf = to_bytes(result, fmt)

        caption = (
            f"✅ *{label}*\n\n"
            f"{img_info(result)}\n\n"
            "🎨 Aur kuch karna hai?"
        )

        if fmt == "PNG":
            await q.message.reply_document(
                document     = buf,
                filename     = "enhanced.png",
                caption      = caption,
                parse_mode   = "Markdown",
                reply_markup = result_menu(),
            )
        else:
            await q.message.reply_photo(
                photo        = buf,
                caption      = caption,
                parse_mode   = "Markdown",
                reply_markup = result_menu(),
            )

        await q.delete_message()
        return

    # unknown
    await q.answer("❓ Unknown action", show_alert=True)


# ─────────────────────────────────────────────────────────────────────────
#  TEXT FALLBACK
# ─────────────────────────────────────────────────────────────────────────

async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📷 Photo bhejo enhance karne ke liye!\n"
        "/help — guide dekhne ke liye"
    )

# ─────────────────────────────────────────────────────────────────────────
#  ERROR HANDLER
# ─────────────────────────────────────────────────────────────────────────

async def on_error(update: object, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Unhandled exception: %s", ctx.error, exc_info=ctx.error)

# ─────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("╔══════════════════════════════════════════╗")
    print("║   🤖 AI Photo Enhancement Bot           ║")
    print("╚══════════════════════════════════════════╝")

    app = Application.builder().token(BOT_TOKEN).build()

    # commands
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("help",   cmd_help))
    app.add_handler(CommandHandler("cancel", cmd_cancel))

    # photo
    app.add_handler(MessageHandler(filters.PHOTO, on_photo))

    # callbacks
    app.add_handler(CallbackQueryHandler(on_callback))

    # text fallback
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    # errors
    app.add_error_handler(on_error)

    print("✅  Bot is running — send a photo on Telegram!")
    print("    Stop: Ctrl+C\n")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
