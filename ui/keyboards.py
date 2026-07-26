from telegram import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

# ─────────────────────────────────────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────────────────────────────────────
def home() -> Markup:
    return Markup([
        [Btn("✨ AI Enhance",  callback_data="m_enhance"),
         Btn("💡 Relight",     callback_data="m_relight")],
        [Btn("🔍 Upscale ×2",  callback_data="up_2"),
         Btn("🔍 Upscale ×4",  callback_data="up_4")],
        [Btn("📏 Enlarge → 12MP", callback_data="enlarge")],
        [Btn("❌ Cancel",       callback_data="cancel")],
    ])

# ─────────────────────────────────────────────────────────────────────────
#  ENHANCE SUB-MENU
# ─────────────────────────────────────────────────────────────────────────
def enhance_menu() -> Markup:
    return Markup([
        [Btn("⚡ Auto Enhance",       callback_data="e_auto"),
         Btn("🖼️ Deep Restore",       callback_data="e_restore")],
        [Btn("👤 Portrait Retouch",   callback_data="e_portrait"),
         Btn("🌄 HDR Look",           callback_data="e_hdr")],
        [Btn("🌙 Night Fix",          callback_data="e_night"),
         Btn("🌈 Vivid Colours",      callback_data="e_vivid")],
        [Btn("🔇 Denoise",            callback_data="e_denoise"),
         Btn("🔪 Sharpen",            callback_data="e_sharpen")],
        [Btn("↩️ Back",               callback_data="home")],
    ])

# ─────────────────────────────────────────────────────────────────────────
#  RELIGHT SUB-MENU
# ─────────────────────────────────────────────────────────────────────────
def relight_menu() -> Markup:
    return Markup([
        [Btn("🤍 Studio White",       callback_data="r_studio"),
         Btn("🌅 Golden Hour",        callback_data="r_golden")],
        [Btn("🎭 Dramatic Shadow",    callback_data="r_dramatic"),
         Btn("💄 Soft Beauty",        callback_data="r_beauty")],
        [Btn("🌈 Neon Night",         callback_data="r_neon"),
         Btn("🌙 Moonlight",          callback_data="r_moon")],
        [Btn("🕯️ Candlelight",        callback_data="r_candle"),
         Btn("🌿 Forest Green",       callback_data="r_forest")],
        [Btn("↩️ Back",               callback_data="home")],
    ])

# ─────────────────────────────────────────────────────────────────────────
#  AFTER RESULT
# ─────────────────────────────────────────────────────────────────────────
def result_menu() -> Markup:
    return Markup([
        [Btn("✨ Enhance Again",  callback_data="m_enhance"),
         Btn("💡 Relight",        callback_data="m_relight")],
        [Btn("🔍 Upscale ×2",    callback_data="up_2"),
         Btn("🔍 Upscale ×4",    callback_data="up_4")],
        [Btn("📏 Enlarge → 12MP", callback_data="enlarge"),
         Btn("✅ Done",           callback_data="cancel")],
    ])
