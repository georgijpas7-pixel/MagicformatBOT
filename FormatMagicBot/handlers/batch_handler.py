from telegram import Update
from telegram.ext import ContextTypes
from config import FREE_BATCH_MAX, PRO_BATCH_MAX
from keyboards.menu import batch_add_more, batch_format_menu, main_menu, back_button, conversion_menu
from services.batch_manager import batch_manager
from services.pro_checker import pro_checker
from services.converter import convert_image
import zipfile
from io import BytesIO
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def add_to_batch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    current_image = context.user_data.get('current_image')
    current_format = context.user_data.get('current_format')
    current_quality = context.user_data.get('current_quality', 75)
    current_ico_size = context.user_data.get('current_ico_size', 64)

    if not current_image:
        await query.edit_message_text("Нет изображения для добавления.", reply_markup=back_button())
        return

    is_pro_user = pro_checker.is_pro(user_id)
    max_batch = PRO_BATCH_MAX if is_pro_user else FREE_BATCH_MAX

    batch = batch_manager.get_batch(user_id)
    if len(batch['images']) >= max_batch:
        await query.edit_message_text(
            f"Лимит пакета: {max_batch} фото.\n\nБесплатно: до {FREE_BATCH_MAX} фото\nPRO: до {PRO_BATCH_MAX} фото\n\nКупить PRO: /buy_pro",
            reply_markup=back_button()
        )
        return

    batch_manager.add_image(user_id, current_image, current_format)
    new_count = len(batch_manager.get_batch(user_id)['images'])

    context.user_data['prev_conversion_text'] = (
        f"Формат: {current_format.upper()}\nКачество: {current_quality}%\nICO: {current_ico_size}px\n\nВыберите действие:"
    )
    context.user_data['prev_conversion_markup'] = conversion_menu(
        current_quality, current_ico_size)

    await query.edit_message_text(
        f"Фото добавлено в пакет!\n\nВ пакете: {new_count}/{max_batch} фото.\n\nЧто дальше?",
        reply_markup=batch_add_more()
    )


async def batch_add_more_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['waiting_for_batch'] = True
    context.user_data['waiting_for_image'] = False
    await query.edit_message_text(
        "📤 Режим добавления фото в пакет включён.\n\nПросто отправляйте фото — они будут автоматически добавляться в пакет.\n\nКогда закончите, нажмите «Готово».",
        reply_markup=back_button()
    )


async def batch_back_to_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prev_text = context.user_data.get('prev_conversion_text')
    prev_markup = context.user_data.get('prev_conversion_markup')

    if prev_text and prev_markup:
        await query.edit_message_text(prev_text, reply_markup=prev_markup)
        context.user_data.pop('prev_conversion_text', None)
        context.user_data.pop('prev_conversion_markup', None)
    else:
        from handlers.start_handler import START_TEXT
        await query.edit_message_text(START_TEXT, reply_markup=main_menu())


async def batch_start_convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    batch = batch_manager.get_batch(user_id)

    if not batch['images']:
        await query.edit_message_text("Пакет пуст. Сначала добавьте фото.", reply_markup=back_button())
        return

    context.user_data['batch_quality'] = context.user_data.get(
        'current_quality', 75)
    context.user_data['batch_ico_size'] = context.user_data.get(
        'current_ico_size', 64)

    is_pro_user = pro_checker.is_pro(user_id)
    max_batch = PRO_BATCH_MAX if is_pro_user else FREE_BATCH_MAX

    await query.edit_message_text(
        f"Пакет: {len(batch['images'])}/{max_batch} фото\n\nКачество: {context.user_data['batch_quality']}%\nICO размер: {context.user_data['batch_ico_size']}px\n\nВыберите формат для конвертации:",
        reply_markup=batch_format_menu()
    )


async def batch_set_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    target = query.data.split('_')[2]
    user_id = update.effective_user.id
    batch = batch_manager.get_batch(user_id)

    if not batch['images']:
        await query.edit_message_text("Пакет пуст.", reply_markup=back_button())
        return

    quality = context.user_data['batch_quality']
    ico_size = context.user_data['batch_ico_size']
    is_pro_user = pro_checker.is_pro(user_id)

    if quality > 75 and not is_pro_user:
        await query.edit_message_text(f"Качество {quality}% доступно только в PRO!\nКупить PRO: /buy_pro", reply_markup=back_button())
        return

    if target == "ICO" and ico_size > 64 and not is_pro_user:
        await query.edit_message_text(f"Размер ICO {ico_size}px доступен только в PRO!\nКупить PRO: /buy_pro", reply_markup=back_button())
        return

    await query.edit_message_text("⏳ Конвертирую пакет... Это может занять время.")

    try:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for idx, img_bytes in enumerate(batch['images']):
                converted = await convert_image(
                    img_bytes,
                    target,
                    context.user_data['batch_quality'],
                    context.user_data['batch_ico_size']
                )
                ext = target.lower()
                if ext == "jpeg":
                    ext = "jpg"
                zf.writestr(f"image_{idx+1}.{ext}", converted)

        zip_buffer.seek(0)

        await query.message.reply_document(
            document=zip_buffer,
            filename=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            caption=f"Пакет из {len(batch['images'])} фото конвертирован в {target}"
        )

        batch_manager.clear_batch(user_id)
        context.user_data.pop('batch_quality', None)
        context.user_data.pop('batch_ico_size', None)
        context.user_data['waiting_for_image'] = True
        context.user_data['waiting_for_batch'] = False

        from handlers.start_handler import START_TEXT
        await query.message.reply_text(START_TEXT, reply_markup=main_menu())
        await query.delete_message()

    except Exception as e:
        logger.error(f"Batch error: {e}")
        await query.edit_message_text("Ошибка при конвертации пакета.", reply_markup=back_button())


async def batch_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    batch_manager.clear_batch(user_id)
    context.user_data.pop('batch_quality', None)
    context.user_data.pop('batch_ico_size', None)
    context.user_data['waiting_for_image'] = False
    context.user_data['waiting_for_batch'] = False

    from handlers.start_handler import START_TEXT
    await query.message.reply_text(START_TEXT, reply_markup=main_menu())
    await query.delete_message()
