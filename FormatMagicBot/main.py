import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TOKEN, BOT_VERSION, BOT_AUTHOR
from handlers.start_handler import start
from handlers.convert_handler import handle_image
from handlers.callback_handler import callback_handler
from handlers.status_handler import status_command, activate_pro
from handlers.payment_handler import buy_pro

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    app = Application.builder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("buy_pro", buy_pro))
    app.add_handler(CommandHandler("activate", activate_pro))  # <--- ДОБАВЛЕНО

    # Обработчики сообщений
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.Document.IMAGE, handle_image))
    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info(f"🤖 {BOT_AUTHOR} | {BOT_VERSION}")
    logger.info("Бот запущен. DonationAlerts + ручная активация")

    app.run_polling(allowed_updates=[])


if __name__ == "__main__":
    main()
