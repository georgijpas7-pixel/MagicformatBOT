from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from config import DONATIONALERTS_URL, PRO_PRICE
from keyboards.menu import back_button
from services.pro_checker import pro_checker


def get_pro_text(user_id):
    return (
        f"👑 PRO подписка — {PRO_PRICE} ₽ на 30 дней\n\n"
        f"Что даёт PRO:\n"
        f"• 🎚 Качество до 100% (вместо 75%)\n"
        f"• 📏 Размер ICO до 256px (вместо 64px)\n"
        f"• 📦 Пакеты до 50 фото (вместо 3)\n"
        f"• 🔧 Изменение размера\n"
        f"• ⭐ Приоритетная поддержка\n\n"
        f"Оплатить: {DONATIONALERTS_URL}\n\n"
        f"❗️ ИНСТРУКЦИЯ:\n"
        f"1. Перейдите по ссылке\n"
        f"2. Введите сумму {PRO_PRICE} ₽\n"
        f"3. В комментарий вставьте ваш Telegram ID: {user_id}\n"
        f"4. Нажмите «Отправить»\n"
        f"5. Напишите администратору /check_payment\n\n"
        f"🕐 Активация происходит вручную.\n"
        f"💬 По вопросам: @GdToper"
    )


async def buy_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if pro_checker.is_pro(user_id):
        expiry = pro_checker.get_expiry_date(user_id)
        days_left = (expiry - datetime.now()).days if expiry else 0
        await update.message.reply_text(
            f"👑 У вас уже есть PRO подписка!\n\n"
            f"✅ Действует до: {expiry.strftime('%d.%m.%Y')}\n"
            f"📆 Осталось дней: {days_left}\n\n"
            f"Спасибо за поддержку! ❤️"
        )
        return

    await update.message.reply_text(
        get_pro_text(user_id),
        disable_web_page_preview=True,
        reply_markup=back_button()
    )


async def buy_pro_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if pro_checker.is_pro(user_id):
        expiry = pro_checker.get_expiry_date(user_id)
        days_left = (expiry - datetime.now()).days if expiry else 0
        await query.edit_message_text(
            f"👑 У вас уже есть PRO подписка!\n\n"
            f"✅ Действует до: {expiry.strftime('%d.%m.%Y')}\n"
            f"📆 Осталось дней: {days_left}\n\n"
            f"Спасибо за поддержку! ❤️"
        )
        return

    await query.edit_message_text(
        get_pro_text(user_id),
        disable_web_page_preview=True,
        reply_markup=back_button()
    )
