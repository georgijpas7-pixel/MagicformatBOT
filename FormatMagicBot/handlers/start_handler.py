from telegram import Update
from telegram.ext import ContextTypes
from keyboards.menu import main_menu, pro_placeholder, back_button

START_TEXT = (
    "🎨 **FormatMagicBot — конвертер изображений**\n\n"
    "Мгновенная конвертация без потери качества прямо в Telegram.\n\n"
    "🖼 **Поддерживаемые форматы:**\n"
    "JPG, PNG, BMP, ICO, WEBP, GIF\n\n"
    "🔧 **Что умеет:**\n"
    "• Конвертировать в любой формат\n"
    "• Обрабатывать до 3 фото за раз\n"
    "• Настраивать качество и размер ICO\n"
    "• Работать с пакетами\n\n"
    "🆓 **Бесплатно:**\n"
    "• Качество до 75%\n"
    "• ICO до 64px\n"
    "• Пакеты до 3 фото\n\n"
    "👑 **PRO (скоро):**\n"
    "• Качество до 100%\n"
    "• ICO до 256px\n"
    "• Пакеты до 50 фото\n"
    "• Приоритетная поддержка\n\n"
    "📤 Нажмите **«Начать работу бесплатно»** и отправьте первое изображение."
)

ABOUT_TEXT = (
    "ℹ️ **О боте**\n\n"
    f"Версия: 2.0\n"
    f"Автор: @GdToper\n\n"
    "Бот создан для быстрой и удобной конвертации изображений.\n"
    "Все базовые функции бесплатны.\n\n"
    "📞 По вопросам: @GdToper"
)

PRO_TEXT = (
    "👑 **PRO подписка**\n\n"
    "Скоро появится! Следите за обновлениями.\n\n"
    "Пока все функции доступны бесплатно в ограниченном режиме:\n"
    "• Качество до 75%\n"
    "• ICO до 64px\n"
    "• Пакеты до 3 фото\n\n"
    "О дате запуска PRO сообщим дополнительно."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(START_TEXT, parse_mode="Markdown", reply_markup=main_menu())


async def start_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['prev_text'] = query.message.text
    context.user_data['prev_markup'] = main_menu()
    context.user_data['waiting_for_image'] = True
    await query.edit_message_text(
        "📤 **Отправьте любое изображение**\n\nПоддерживаются: JPG, PNG, BMP, ICO, WEBP, GIF",
        parse_mode="Markdown",
        reply_markup=back_button()
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['prev_text'] = query.message.text
    context.user_data['prev_markup'] = main_menu()
    await query.edit_message_text(ABOUT_TEXT, parse_mode="Markdown", reply_markup=pro_placeholder())


async def buy_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['prev_text'] = query.message.text
    context.user_data['prev_markup'] = main_menu()
    await query.edit_message_text(PRO_TEXT, parse_mode="Markdown", reply_markup=pro_placeholder())


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prev_text = context.user_data.get('prev_text')
    prev_markup = context.user_data.get('prev_markup')
    if prev_text and prev_markup:
        await query.edit_message_text(prev_text, parse_mode="Markdown", reply_markup=prev_markup)
        context.user_data.pop('prev_text', None)
        context.user_data.pop('prev_markup', None)
    else:
        await query.edit_message_text(START_TEXT, parse_mode="Markdown", reply_markup=main_menu())
