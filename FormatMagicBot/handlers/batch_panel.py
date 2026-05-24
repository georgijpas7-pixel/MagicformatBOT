from telegram import Update
from telegram.ext import ContextTypes
from keyboards.menu import batch_panel, main_menu, back_button
from services.batch_manager import batch_manager
from services.pro_checker import pro_checker
from config import FREE_BATCH_MAX, PRO_BATCH_MAX


async def batch_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    batch = batch_manager.get_batch(user_id)
    count = len(batch['images'])

    if pro_checker.is_pro(user_id):
        max_batch = PRO_BATCH_MAX
    else:
        max_batch = FREE_BATCH_MAX

    if count == 0:
        await query.edit_message_text(
            "📦 Пакет пуст\n\nДобавьте фото в пакет через меню конвертации.",
            reply_markup=back_button()
        )
        return

    await query.edit_message_text(
        f"📦 Управление пакетом\n\nВ пакете: {count}/{max_batch} фото\n\nВыберите действие:",
        reply_markup=batch_panel(count, max_batch)
    )


async def batch_clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    batch_manager.clear_batch(user_id)

    from handlers.start_handler import START_TEXT
    await query.message.reply_text(START_TEXT, reply_markup=main_menu())
    await query.delete_message()
