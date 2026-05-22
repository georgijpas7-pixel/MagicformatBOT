from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import QUALITY_OPTIONS, ICO_SIZE_OPTIONS


def main_menu():
    keyboard = [
        [InlineKeyboardButton("🚀 Начать работу бесплатно",
                              callback_data="start_free")],
        [InlineKeyboardButton("📦 Работа с пакетом",
                              callback_data="batch_panel")],
        [InlineKeyboardButton("👑 Купить PRO", callback_data="buy_pro")],
        [InlineKeyboardButton("ℹ️ Инфо о боте", callback_data="about")],
        [InlineKeyboardButton("📊 Мой статус", callback_data="status")]
    ]
    return InlineKeyboardMarkup(keyboard)


def conversion_menu(quality, ico_size):
    keyboard = [
        [
            InlineKeyboardButton("📸 JPG", callback_data="convert_JPG"),
            InlineKeyboardButton("🖼 PNG", callback_data="convert_PNG"),
            InlineKeyboardButton("🎨 ICO", callback_data="convert_ICO"),
            InlineKeyboardButton("🌐 WEBP", callback_data="convert_WEBP")
        ],
        [
            InlineKeyboardButton(
                f"🎚 Качество: {quality}%", callback_data="quality_settings"),
            InlineKeyboardButton(
                f"📏 ICO: {ico_size}px", callback_data="ico_settings")
        ],
        [
            InlineKeyboardButton("📦 Добавить в пакет",
                                 callback_data="add_to_batch"),
            InlineKeyboardButton("◀️ Назад", callback_data="back")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def quality_menu(current):
    keyboard = []
    for q in QUALITY_OPTIONS:
        emoji = "✅" if q == current else "  "
        keyboard.append([InlineKeyboardButton(
            f"{emoji} {q}%", callback_data=f"set_quality_{q}")])
    keyboard.append([InlineKeyboardButton(
        "◀️ Назад", callback_data="back_to_conversion")])
    return InlineKeyboardMarkup(keyboard)


def ico_menu(current):
    keyboard = []
    for size in ICO_SIZE_OPTIONS:
        emoji = "✅" if size == current else "  "
        keyboard.append([InlineKeyboardButton(
            f"{emoji} {size}x{size}", callback_data=f"set_ico_{size}")])
    keyboard.append([InlineKeyboardButton(
        "◀️ Назад", callback_data="back_to_conversion")])
    return InlineKeyboardMarkup(keyboard)


def batch_add_more_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Добавить ещё", callback_data="batch_add_more"),
            InlineKeyboardButton("🔄 Начать конвертацию",
                                 callback_data="batch_start_convert")
        ],
        [InlineKeyboardButton(
            "◀️ Назад к фото", callback_data="batch_back_to_conversion")],
        [InlineKeyboardButton("❌ Отменить", callback_data="batch_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def batch_format_menu():
    keyboard = [
        [InlineKeyboardButton("📸 JPG", callback_data="batch_format_JPG")],
        [InlineKeyboardButton("🖼 PNG", callback_data="batch_format_PNG")],
        [InlineKeyboardButton("🎨 ICO", callback_data="batch_format_ICO")],
        [InlineKeyboardButton("🌐 WEBP", callback_data="batch_format_WEBP")],
        [InlineKeyboardButton("◀️ Назад", callback_data="batch_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def batch_panel(batch_count, max_batch):
    keyboard = [
        [InlineKeyboardButton(
            f"📦 В пакете: {batch_count}/{max_batch} фото", callback_data="noop")],
        [InlineKeyboardButton("🔄 Конвертировать пакет",
                              callback_data="batch_start_convert")],
        [InlineKeyboardButton("🗑 Очистить пакет",
                              callback_data="batch_clear")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)


def pro_placeholder():
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back")]]
    return InlineKeyboardMarkup(keyboard)


def back_button():
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back")]]
    return InlineKeyboardMarkup(keyboard)
