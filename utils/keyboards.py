from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("✨ AI Auto Enhance", callback_data="ai_auto"),
            InlineKeyboardButton("📐 AI Upscale 2x", callback_data="upscale_2x"),
        ],
        [
            InlineKeyboardButton("🎨 Remove Background", callback_data="remove_bg"),
            InlineKeyboardButton("🔵 Blur Background", callback_data="blur_bg"),
        ],
        [
            InlineKeyboardButton("💡 AI Relight", callback_data="relight_menu"),
            InlineKeyboardButton("🖼️ Filters", callback_data="filters_menu"),
        ],
        [
            InlineKeyboardButton("👤 Portrait Enhance", callback_data="portrait"),
            InlineKeyboardButton("🌄 HDR Effect", callback_data="hdr"),
        ],
        [
            InlineKeyboardButton("🌙 Night → Day", callback_data="night_day"),
            InlineKeyboardButton("📐 Upscale 4x", callback_data="upscale_4x"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)

def filters_menu():
    keyboard = [
        [
            InlineKeyboardButton("✏️ Pencil Sketch", callback_data="f_pencil"),
            InlineKeyboardButton("🎨 Cartoon", callback_data="f_cartoon"),
        ],
        [
            InlineKeyboardButton("🖌️ Oil Painting", callback_data="f_oil"),
            InlineKeyboardButton("💧 Watercolor", callback_data="f_watercolor"),
        ],
        [
            InlineKeyboardButton("⚡ Glitch", callback_data="f_glitch"),
            InlineKeyboardButton("🌈 Neon Glow", callback_data="f_neon"),
        ],
        [
            InlineKeyboardButton("📽️ Vintage Film", callback_data="f_vintage"),
            InlineKeyboardButton("🤖 Cyberpunk", callback_data="f_cyberpunk"),
        ],
        [
            InlineKeyboardButton("🎭 Duotone", callback_data="f_duotone"),
            InlineKeyboardButton("🔮 Pop Art", callback_data="f_popart"),
        ],
        [
            InlineKeyboardButton("📷 Infrared", callback_data="f_infrared"),
            InlineKeyboardButton("🪞 Mirror", callback_data="f_mirror"),
        ],
        [
            InlineKeyboardButton("🟫 Sepia", callback_data="f_sepia"),
            InlineKeyboardButton("⬛ Pixelate", callback_data="f_pixelate"),
        ],
        [
            InlineKeyboardButton("🌑 Vignette", callback_data="f_vignette"),
            InlineKeyboardButton("↩️ Back", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def relight_menu():
    keyboard = [
        [
            InlineKeyboardButton("💡 Studio Light", callback_data="r_studio"),
            InlineKeyboardButton("🌅 Golden Hour", callback_data="r_golden"),
        ],
        [
            InlineKeyboardButton("🎭 Dramatic", callback_data="r_dramatic"),
            InlineKeyboardButton("✨ Soft Beauty", callback_data="r_beauty"),
        ],
        [
            InlineKeyboardButton("🌈 Neon Light", callback_data="r_neon"),
            InlineKeyboardButton("↩️ Back", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def video_menu():
    keyboard = [
        [
            InlineKeyboardButton("✨ Auto Enhance", callback_data="v_auto"),
            InlineKeyboardButton("🔇 Denoise", callback_data="v_denoise"),
        ],
        [
            InlineKeyboardButton("🌄 HDR Effect", callback_data="v_hdr"),
            InlineKeyboardButton("🔍 Sharpen", callback_data="v_sharpen"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)

def after_enhance_menu():
    keyboard = [
        [
            InlineKeyboardButton("🔄 More Enhancements", callback_data="back_main"),
            InlineKeyboardButton("🎨 Apply Filter", callback_data="filters_menu"),
        ],
        [
            InlineKeyboardButton("💡 Change Lighting", callback_data="relight_menu"),
            InlineKeyboardButton("✅ Done", callback_data="done"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
