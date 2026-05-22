from telegram import Update
from telegram.ext import ContextTypes
from handlers.start_handler import start_free, about, back
from handlers.convert_handler import quality_settings, ico_settings, set_quality, set_ico_size, back_to_conversion, perform_conversion
from handlers.batch_handler import add_to_batch, batch_add_more_handler, batch_start_convert, batch_set_format, batch_cancel, batch_back_to_conversion
from handlers.batch_panel import batch_panel_handler, batch_clear_handler
from handlers.status_handler import status_callback
from handlers.payment_handler import buy_pro_callback


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # Главное меню
    if data == "start_free":
        await start_free(update, context)
    elif data == "about":
        await about(update, context)
    elif data == "buy_pro":
        await buy_pro_callback(update, context)
    elif data == "back":
        await back(update, context)

    # Пакетная панель
    elif data == "batch_panel":
        await batch_panel_handler(update, context)
    elif data == "batch_clear":
        await batch_clear_handler(update, context)

    # Настройки качества и ICO
    elif data == "quality_settings":
        await quality_settings(update, context)
    elif data == "ico_settings":
        await ico_settings(update, context)
    elif data.startswith("set_quality_"):
        await set_quality(update, context)
    elif data.startswith("set_ico_"):
        await set_ico_size(update, context)
    elif data == "back_to_conversion":
        await back_to_conversion(update, context)

    # Конвертация
    elif data.startswith("convert_"):
        await perform_conversion(update, context)

    # Пакетная обработка
    elif data == "add_to_batch":
        await add_to_batch(update, context)
    elif data == "batch_add_more":
        await batch_add_more_handler(update, context)
    elif data == "batch_back_to_conversion":
        await batch_back_to_conversion(update, context)
    elif data == "batch_start_convert":
        await batch_start_convert(update, context)
    elif data.startswith("batch_format_"):
        await batch_set_format(update, context)
    elif data == "batch_cancel":
        await batch_cancel(update, context)

    # Статус
    elif data == "status":
        await status_callback(update, context)

    # Заглушка
    elif data == "noop":
        await query.answer("ℹ️ Информация", show_alert=False)

    else:
        await query.answer("Неизвестная команда")
