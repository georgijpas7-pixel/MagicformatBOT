from telegram import Update
from telegram.ext import ContextTypes
from io import BytesIO
from PIL import Image
from datetime import datetime
from config import ALLOWED_FORMATS, MAX_FILE_SIZE_BYTES, FREE_BATCH_MAX, PRO_BATCH_MAX
from keyboards.menu import conversion_menu, quality_menu, ico_menu, main_menu, batch_add_more, back_button
from services.pro_checker import pro_checker
from services.batch_manager import batch_manager
import logging

logger = logging.getLogger(__name__)


async def add_to_batch_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Автоматическое добавление фото в пакет (режим Добавить ещё)"""
    user_id = update.effective_user.id

    if not update.message.photo and not update.message.document:
        await update.message.reply_text("❌ Пожалуйста, отправьте изображение.")
        return

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        file_bytes = await photo_file.download_as_bytearray()
    else:
        doc = update.message.document
        if not doc.mime_type or not doc.mime_type.startswith('image/'):
            await update.message.reply_text("❌ Поддерживаются только изображения.")
            return
        if doc.file_size and doc.file_size > MAX_FILE_SIZE_BYTES:
            await update.message.reply_text(f"❌ Файл слишком большой (>10 МБ)")
            return
        photo_file = await doc.get_file()
        file_bytes = await photo_file.download_as_bytearray()

    # Определяем формат
    img = Image.open(BytesIO(file_bytes))
    original_format = img.format.lower() if img.format else 'unknown'
    display_format = original_format.upper()

    # Обработка GIF
    if original_format == 'gif':
        await update.message.reply_text("⚠️ Обнаружен GIF. Будет использован первый кадр.")
        img.seek(0)
        first_frame = img.convert("RGBA")
        output = BytesIO()
        first_frame.save(output, format='PNG')
        file_bytes = output.getvalue()
        original_format = 'gif'
        display_format = 'GIF (первый кадр)'

    if original_format not in ALLOWED_FORMATS:
        await update.message.reply_text(f"❌ Формат {display_format} не поддерживается.")
        return

    is_pro_user = pro_checker.is_pro(user_id)
    max_batch = PRO_BATCH_MAX if is_pro_user else FREE_BATCH_MAX

    batch = batch_manager.get_batch(user_id)
    if len(batch['images']) >= max_batch:
        await update.message.reply_text(f"❌ Лимит пакета: {max_batch} фото.\n\nКупить PRO: /buy_pro")
        return

    batch_manager.add_image(user_id, file_bytes, original_format)
    new_count = len(batch_manager.get_batch(user_id)['images'])

    await update.message.reply_text(
        f"✅ Фото добавлено в пакет!\n\n📦 В пакете: {new_count}/{max_batch} фото.\n\nОтправьте ещё или нажмите «Готово».",
        reply_markup=batch_add_more()
    )
    context.user_data['waiting_for_batch'] = True


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Режим автоматического добавления в пакет
    if context.user_data.get('waiting_for_batch'):
        await add_to_batch_auto(update, context)
        return

    if not context.user_data.get('waiting_for_image'):
        context.user_data['waiting_for_image'] = True

    # Проверка на наличие фото/документа
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(
            "❌ Ошибка!\n\nПоддерживаются только изображения:\n• JPG, PNG, BMP, ICO, WEBP, GIF\n\nПожалуйста, отправьте изображение."
        )
        return

    # Получение файла
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        file_bytes = await photo_file.download_as_bytearray()
        file_type = 'photo'
    else:
        doc = update.message.document
        if not doc.mime_type or not doc.mime_type.startswith('image/'):
            await update.message.reply_text(
                f"❌ Ошибка!\n\nФормат `{doc.mime_type}` не поддерживается.\nПоддерживаются: JPG, PNG, BMP, ICO, WEBP, GIF"
            )
            return
        if doc.file_size and doc.file_size > MAX_FILE_SIZE_BYTES:
            await update.message.reply_text(f"❌ Файл слишком большой (>10 МБ)")
            return
        photo_file = await doc.get_file()
        file_bytes = await photo_file.download_as_bytearray()
        file_type = 'document'

    # Отладка
    print(f"DEBUG: file_type = {file_type}")
    if file_type == 'document':
        print(f"DEBUG: mime_type = {update.message.document.mime_type}")

    # Определение формата через PIL
    img = Image.open(BytesIO(file_bytes))
    original_format = img.format.lower() if img.format else 'unknown'
    print(f"DEBUG: PIL format = {original_format}")

    # Обработка GIF
    is_gif = (original_format == 'gif')
    display_format = original_format.upper()

    if is_gif:
        # Проверка на анимированный GIF
        is_animated = False
        try:
            img.seek(1)
            is_animated = True
        except EOFError:
            is_animated = False
        img.seek(0)

        if is_animated:
            await update.message.reply_text("⚠️ Обнаружен анимированный GIF. Будет использован первый кадр.")
        else:
            await update.message.reply_text("⚠️ Обнаружен статичный GIF. Будет использован первый кадр.")

        # Конвертируем первый кадр в PNG
        first_frame = img.convert("RGBA")
        output = BytesIO()
        first_frame.save(output, format='PNG')
        file_bytes = output.getvalue()
        original_format = 'gif'
        display_format = 'GIF (первый кадр)'

    # Проверка поддерживаемого формата
    if original_format not in ALLOWED_FORMATS:
        await update.message.reply_text(
            f"❌ Ошибка!\n\nФормат `{display_format}` не поддерживается.\nДоступные форматы: {', '.join(ALLOWED_FORMATS).upper()}"
        )
        return

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        await update.message.reply_text(f"❌ Файл слишком большой (>10 МБ)")
        return

    # Инициализация пакета
    if user_id not in batch_manager.batches:
        batch_manager.batches[user_id] = {
            'images': [], 'formats': [], 'last_active': datetime.now()}
    else:
        batch_manager.batches[user_id]['last_active'] = datetime.now()

    # Настройки по умолчанию
    if 'current_quality' not in context.user_data:
        context.user_data['current_quality'] = 75
    if 'current_ico_size' not in context.user_data:
        context.user_data['current_ico_size'] = 64

    context.user_data['current_image'] = file_bytes
    context.user_data['current_format'] = original_format
    context.user_data['waiting_for_image'] = False

    await update.message.reply_text(
        f"🖼 Получено: {display_format}\n🎚 Качество: {context.user_data['current_quality']}%\n📏 ICO: {context.user_data['current_ico_size']}px\n\nВыберите действие:",
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

    if quality > 75 and not pro_checker.is_pro(user_id):
        await query.edit_message_text(
            f"❌ **Ошибка!**\n\n"
            f"Качество {quality}% доступно только в PRO!\n\n"
            f"Ваша подписка истекла или неактивна.\n"
            f"💰 Купить PRO: /buy_pro",
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

    if size > 64 and not pro_checker.is_pro(user_id):
        await query.edit_message_text(
            f"❌ **Ошибка!**\n\n"
            f"Размер ICO {size}px доступен только в PRO!\n\n"
            f"Ваша подписка истекла или неактивна.\n"
            f"💰 Купить PRO: /buy_pro",
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

    if quality > 75 and not pro_checker.is_pro(user_id):
        await query.edit_message_text(f"❌ Качество {quality}% доступно только в PRO!\n\nКупить PRO: /buy_pro")
        return

    if target == "ICO" and ico_size > 64 and not pro_checker.is_pro(user_id):
        await query.edit_message_text(f"❌ Размер ICO {ico_size}px доступен только в PRO!\n\nКупить PRO: /buy_pro")
        return

    await query.edit_message_text("⏳ Конвертирую...")

    img = Image.open(BytesIO(context.user_data['current_image']))
    output = BytesIO()

    # Конвертация в GIF
    if target == "GIF":
        img = img.convert("RGB")
        img.save(output, format="GIF", save_all=True, duration=100, loop=0)

    elif target == "ICO":
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
    if ext == "gif":
        ext = "gif"

    await query.message.reply_document(
        document=output,
        filename=f"converted.{ext}",
        caption=f"✅ {context.user_data['current_format'].upper()} → {target}\n🎚 Качество: {quality}%"
    )

    from handlers.start_handler import START_TEXT
    await query.message.reply_text(START_TEXT, reply_markup=main_menu())
    await query.delete_message()
    context.user_data['waiting_for_image'] = True
