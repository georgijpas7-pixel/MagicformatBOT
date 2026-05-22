class Navigation:
    @staticmethod
    def save_previous(context, text, reply_markup):
        """Сохраняет предыдущее состояние для кнопки Назад"""
        context.user_data['prev_text'] = text
        context.user_data['prev_markup'] = reply_markup

    @staticmethod
    def get_previous(context):
        """Возвращает предыдущее состояние"""
        text = context.user_data.get('prev_text')
        markup = context.user_data.get('prev_markup')
        return text, markup

    @staticmethod
    def clear(context):
        """Очищает сохранённое состояние"""
        context.user_data.pop('prev_text', None)
        context.user_data.pop('prev_markup', None)
