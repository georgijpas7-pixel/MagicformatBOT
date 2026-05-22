from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from config import FREE_QUALITY_MAX, FREE_ICO_MAX, FREE_BATCH_MAX, ADMIN_ID
from keyboards.menu import back_button, main_menu
from services.pro_checker import pro_checker


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

    is_pro = pro_checker.is_pro(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    usage = pro_checker.usage.get(user_id, {})
    today_usage = usage.get(today, 0)

    if is_pro:
        expiry = pro_checker.get_expiry_date(user_id)
        days_left = (expiry - datetime.now()).days if expiry else 0
        status_text = (
            f"👑 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Имя: {first_name}\n"
            f"📛 Username: @{username if username else 'не указан'}\n\n"
            f"🌟 СТАТУС ПОДПИСКИ:\n"
            f"✅ PRO активна\n"
            f"📅 Действует до: {expiry.strftime('%d.%m.%Y')}\n"
            f"📆 Осталось дней: {days_left}\n\n"
            f"🔓 Доступно:\n"
            f"• Качество до 100%\n"
            f"• ICO до 256px\n"
            f"• Пакеты до 50 фото\n\n"
            f"💎 Спасибо за поддержку!"
        )
    else:
        status_text = (
            f"🆓 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Имя: {first_name}\n"
            f"📛 Username: @{username if username else 'не указан'}\n\n"
            f"🌟 СТАТУС ПОДПИСКИ:\n"
            f"🆓 Бесплатный тариф\n\n"
            f"🔓 Доступно сейчас:\n"
            f"• 🎚 Качество до {FREE_QUALITY_MAX}%\n"
            f"• 📏 ICO до {FREE_ICO_MAX}px\n"
            f"• 📦 Пакеты до {FREE_BATCH_MAX} фото\n\n"
            f"📊 Конвертаций сегодня: {today_usage}\n\n"
            f"👑 Купить PRO: /buy_pro"
        )

    await update.message.reply_text(status_text, reply_markup=back_button())


async def status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

    is_pro = pro_checker.is_pro(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    usage = pro_checker.usage.get(user_id, {})
    today_usage = usage.get(today, 0)

    if is_pro:
        expiry = pro_checker.get_expiry_date(user_id)
        days_left = (expiry - datetime.now()).days if expiry else 0
        status_text = (
            f"👑 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Имя: {first_name}\n"
            f"📛 Username: @{username if username else 'не указан'}\n\n"
            f"🌟 СТАТУС ПОДПИСКИ:\n"
            f"✅ PRO активна\n"
            f"📅 Действует до: {expiry.strftime('%d.%m.%Y')}\n"
            f"📆 Осталось дней: {days_left}\n\n"
            f"🔓 Доступно:\n"
            f"• Качество до 100%\n"
            f"• ICO до 256px\n"
            f"• Пакеты до 50 фото\n\n"
            f"💎 Спасибо за поддержку!"
        )
    else:
        status_text = (
            f"🆓 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Имя: {first_name}\n"
            f"📛 Username: @{username if username else 'не указан'}\n\n"
            f"🌟 СТАТУС ПОДПИСКИ:\n"
            f"🆓 Бесплатный тариф\n\n"
            f"🔓 Доступно сейчас:\n"
            f"• 🎚 Качество до {FREE_QUALITY_MAX}%\n"
            f"• 📏 ICO до {FREE_ICO_MAX}px\n"
            f"• 📦 Пакеты до {FREE_BATCH_MAX} фото\n\n"
            f"📊 Конвертаций сегодня: {today_usage}\n\n"
            f"👑 Купить PRO: /buy_pro"
        )

    await query.edit_message_text(status_text, reply_markup=back_button())


async def activate_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Активация PRO подписки (только для администратора)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Доступ запрещён")
        return

    try:
        user_id = int(context.args[0])
        days = int(context.args[1]) if len(context.args) > 1 else 30

        pro_checker.activate_pro(user_id, days)
        expiry = pro_checker.get_expiry_date(user_id)

        await update.message.reply_text(
            f"✅ PRO активирован для пользователя {user_id}\n"
            f"📆 На {days} дней\n"
            f"📅 Действует до: {expiry.strftime('%d.%m.%Y')}"
        )

        # Уведомляем пользователя
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"👑 PRO подписка активирована на {days} дней!\n\n"
                f"✅ Действует до: {expiry.strftime('%d.%m.%Y')}\n\n"
                f"Спасибо за поддержку! ❤️\n\n"
                f"Проверить статус: /status"
            )
        except Exception as e:
            await update.message.reply_text(f"⚠️ Не удалось уведомить пользователя: {e}")

    except (IndexError, ValueError):
        await update.message.reply_text("❌ Используй: /activate 5029334638 30")
