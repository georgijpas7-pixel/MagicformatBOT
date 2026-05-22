from telegram import Update
from telegram.ext import ContextTypes
from keyboards.menu import batch_panel, main_menu, back_button
from services.batch_manager import batch_manager
from config import FREE_BATCH_MAX


async def batch_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    batch = batch_manager.get_batch(user_id)
    count = len(batch['images'])

    if count == 0:
        await query.edit_message_text(
            "📦 **Пакет пуст**\n\nДобавьте фото в пакет через меню конвертации.",
            parse_mode="Markdown",
            reply_markup=back_button()
        )
        return

    await query.edit_message_text(
        f"📦 **Управление пакетом**\n\n"
        f"В пакете: {count}/{FREE_BATCH_MAX} фото\n\n"
        f"Выберите действие:",
        parse_mode="Markdown",
        reply_markup=batch_panel(count, FREE_BATCH_MAX)
    )


async def batch_clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    batch_manager.clear_batch(user_id)

    from handlers.start_handler import START_TEXT
    await query.message.reply_text(START_TEXT, parse_mode="Markdown", reply_markup=main_menu())
    await query.delete_message()
