from telegram import Update
from telegram.ext import ContextTypes
from io import BytesIO
from PIL import Image
from config import ALLOWED_FORMATS, MAX_FILE_SIZE_BYTES
from keyboards.menu import conversion_menu, quality_menu, ico_menu, main_menu
from services.pro_checker import pro_checker
import logging

logger = logging.getLogger(__name__)


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_for_image'):
        await update.message.reply_text("Сначала нажмите «Начать работу бесплатно»", reply_markup=main_menu())
        return

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        file_bytes = await photo_file.download_as_bytearray()
    elif update.message.document:
        doc = update.message.document
        if not doc.mime_type or not doc.mime_type.startswith('image/'):
            await update.message.reply_text("❌ Отправьте изображение!")
            return
        if doc.file_size and doc.file_size > MAX_FILE_SIZE_BYTES:
            await update.message.reply_text("❌ Файл слишком большой (>10 МБ)")
            return
        photo_file = await doc.get_file()
        file_bytes = await photo_file.download_as_bytearray()
    else:
        await update.message.reply_text("❌ Отправьте изображение!")
        return

    img = Image.open(BytesIO(file_bytes))
    original_format = img.format.lower() if img.format else 'unknown'

    if original_format not in ALLOWED_FORMATS:
        await update.message.reply_text(f"❌ Формат {original_format.upper()} не поддерживается")
        return

    context.user_data['current_image'] = file_bytes
    context.user_data['current_format'] = original_format
    context.user_data['current_quality'] = context.user_data.get(
        'current_quality', 75)
    context.user_data['current_ico_size'] = context.user_data.get(
        'current_ico_size', 64)
    context.user_data['waiting_for_image'] = False

    await update.message.reply_text(
        f"🖼 **Получено:** {original_format.upper()}\n"
        f"🎚 Качество: {context.user_data['current_quality']}%\n"
        f"📏 ICO: {context.user_data['current_ico_size']}px\n\n"
        f"Выберите действие:",
        parse_mode="Markdown",
        reply_markup=conversion_menu(
            context.user_data['current_quality'], context.user_data['current_ico_size'])
    )


async def quality_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"🎚 **Выберите качество**\n\nТекущее: {context.user_data['current_quality']}%\n\n⚠️ Качество выше 75% — PRO",
        parse_mode="Markdown",
        reply_markup=quality_menu(context.user_data['current_quality'])
    )


async def ico_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"📏 **Выберите размер ICO**\n\nТекущий: {context.user_data['current_ico_size']}px\n\n⚠️ Размер >64px — PRO",
        parse_mode="Markdown",
        reply_markup=ico_menu(context.user_data['current_ico_size'])
    )


async def set_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quality = int(query.data.split('_')[2])
    user_id = update.effective_user.id

    # Проверка PRO
    if quality > 75:
        if not pro_checker.is_pro(user_id):
            await query.edit_message_text(
                f"❌ **Ошибка!**\n\n"
                f"Качество {quality}% доступно только в PRO!\n\n"
                f"Ваша подписка истекла или неактивна.\n"
                f"💰 Оплатить: /buy_pro",
                parse_mode="Markdown"
            )
            return

    context.user_data['current_quality'] = quality
    await query.edit_message_text(
        f"🖼 **Формат:** {context.user_data['current_format'].upper()}\n🎚 Качество: {quality}%\n📏 ICO: {context.user_data['current_ico_size']}px",
        parse_mode="Markdown",
        reply_markup=conversion_menu(
            quality, context.user_data['current_ico_size'])
    )


async def set_ico_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    size = int(query.data.split('_')[2])
    user_id = update.effective_user.id

    # Проверка PRO
    if size > 64:
        if not pro_checker.is_pro(user_id):
            await query.edit_message_text(
                f"❌ **Ошибка!**\n\n"
                f"Размер ICO {size}px доступен только в PRO!\n\n"
                f"Ваша подписка истекла или неактивна.\n"
                f"💰 Оплатить: /buy_pro",
                parse_mode="Markdown"
            )
            return

    context.user_data['current_ico_size'] = size
    await query.edit_message_text(
        f"🖼 **Формат:** {context.user_data['current_format'].upper()}\n🎚 Качество: {context.user_data['current_quality']}%\n📏 ICO: {size}px",
        parse_mode="Markdown",
        reply_markup=conversion_menu(
            context.user_data['current_quality'], size)
    )


async def back_to_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"🖼 **Формат:** {context.user_data['current_format'].upper()}\n"
        f"🎚 Качество: {context.user_data['current_quality']}%\n"
        f"📏 ICO: {context.user_data['current_ico_size']}px\n\n"
        f"Выберите действие:",
        parse_mode="Markdown",
        reply_markup=conversion_menu(
            context.user_data['current_quality'], context.user_data['current_ico_size'])
    )


async def perform_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    target = query.data.split('_')[1]
    quality = context.user_data['current_quality']
    ico_size = context.user_data['current_ico_size']
    user_id = update.effective_user.id

    # Проверка PRO
    if quality > 75:
        if not pro_checker.is_pro(user_id):
            await query.edit_message_text(
                f"❌ **Ошибка!**\n\n"
                f"Качество {quality}% доступно только в PRO!\n\n"
                f"Ваша подписка истекла или неактивна.\n"
                f"💰 Оплатить: /buy_pro",
                parse_mode="Markdown"
            )
            return

    if target == "ICO" and ico_size > 64:
        if not pro_checker.is_pro(user_id):
            await query.edit_message_text(
                f"❌ **Ошибка!**\n\n"
                f"Размер ICO {ico_size}px доступен только в PRO!\n\n"
                f"Ваша подписка истекла или неактивна.\n"
                f"💰 Оплатить: /buy_pro",
                parse_mode="Markdown"
            )
            return

    await query.edit_message_text("⏳ Конвертирую...")

    img = Image.open(BytesIO(context.user_data['current_image']))
    output = BytesIO()

    if target == "ICO":
        img = img.convert("RGBA")
        img.thumbnail((ico_size, ico_size), Image.Resampling.LANCZOS)
        size = max(img.size)
        square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        x = (size - img.size[0]) // 2
        y = (size - img.size[1]) // 2
        square.paste(img, (x, y))
        square.save(output, format="ICO", sizes=[(size, size)])

    elif target in ["JPG", "JPEG"]:
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = bg
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(output, format="JPEG", quality=quality, optimize=True)

    elif target == "WEBP":
        if img.mode in ("RGBA", "LA"):
            img.save(output, format="WEBP", quality=quality, lossless=False)
        else:
            img = img.convert("RGB")
            img.save(output, format="WEBP", quality=quality)

    else:
        img.save(output, format=target)

    output.seek(0)
    ext = target.lower()
    if ext == "jpeg":
        ext = "jpg"

    await query.message.reply_document(
        document=output,
        filename=f"converted.{ext}",
        caption=f"✅ {context.user_data['current_format'].upper()} → {target}\n🎚 Качество: {quality}%"
    )

    # Отправляем приветственное меню новым сообщением
    from handlers.start_handler import START_TEXT
    await query.message.reply_text(START_TEXT, parse_mode="Markdown", reply_markup=main_menu())
    await query.delete_message()
    context.user_data['waiting_for_image'] = True
