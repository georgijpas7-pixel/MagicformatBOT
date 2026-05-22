import json
import os
from datetime import datetime, timedelta
from config import FREE_QUALITY_MAX, FREE_ICO_MAX, FREE_BATCH_MAX, PRO_QUALITY_MAX, PRO_ICO_MAX, PRO_BATCH_MAX

SUBSCRIPTIONS_FILE = "subscriptions.json"
USAGE_FILE = "usage.json"


class ProChecker:
    def __init__(self):
        self.subscriptions = {}
        self.usage = {}
        self.load_data()

    def load_data(self):
        """Загружает данные из файлов"""
        if os.path.exists(SUBSCRIPTIONS_FILE):
            try:
                with open(SUBSCRIPTIONS_FILE, 'r') as f:
                    data = json.load(f)
                    # Конвертируем строки дат обратно в datetime
                    for user_id, expiry_str in data.items():
                        self.subscriptions[int(user_id)] = datetime.fromisoformat(
                            expiry_str)
            except:
                pass

        if os.path.exists(USAGE_FILE):
            try:
                with open(USAGE_FILE, 'r') as f:
                    self.usage = json.load(f)
                    # Конвертируем ключи user_id из строк в int
                    self.usage = {int(k): v for k, v in self.usage.items()}
            except:
                pass

    def save_data(self):
        """Сохраняет данные в файлы"""
        # Сохраняем подписки
        subscriptions_to_save = {}
        for user_id, expiry in self.subscriptions.items():
            subscriptions_to_save[user_id] = expiry.isoformat()

        with open(SUBSCRIPTIONS_FILE, 'w') as f:
            json.dump(subscriptions_to_save, f, indent=2)

        # Сохраняем использование
        with open(USAGE_FILE, 'w') as f:
            json.dump(self.usage, f, indent=2)

    def is_pro(self, user_id):
        if user_id in self.subscriptions:
            if datetime.now() < self.subscriptions[user_id]:
                return True
            else:
                del self.subscriptions[user_id]
                self.save_data()
        return False

    def activate_pro(self, user_id, days=30):
        expiry = datetime.now() + timedelta(days=days)
        self.subscriptions[user_id] = expiry
        self.save_data()
        return expiry

    def get_expiry_date(self, user_id):
        return self.subscriptions.get(user_id)

    def can_use_quality(self, user_id, quality):
        if self.is_pro(user_id):
            return quality <= PRO_QUALITY_MAX, None
        return quality <= FREE_QUALITY_MAX, FREE_QUALITY_MAX

    def can_use_ico_size(self, user_id, size):
        if self.is_pro(user_id):
            return size <= PRO_ICO_MAX, None
        return size <= FREE_ICO_MAX, FREE_ICO_MAX

    def can_use_batch_size(self, user_id, batch_count):
        if self.is_pro(user_id):
            return batch_count <= PRO_BATCH_MAX, None
        return batch_count <= FREE_BATCH_MAX, FREE_BATCH_MAX

    def can_use_resize(self, user_id):
        return self.is_pro(user_id)

    def increment_usage(self, user_id):
        today = datetime.now().strftime("%Y-%m-%d")
        if user_id not in self.usage:
            self.usage[user_id] = {}
        if today not in self.usage[user_id]:
            self.usage[user_id][today] = 0
        self.usage[user_id][today] += 1
        self.save_data()

    def get_today_usage(self, user_id):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.usage.get(user_id, {}).get(today, 0)

    def get_free_limit_message(self, limit_type, limit_value):
        messages = {
            'quality': f"❌ Качество выше {limit_value}% доступно только в PRO!\n💰 Купить PRO: /buy_pro",
            'ico': f"❌ Размер ICO более {limit_value}px доступен только в PRO!\n💰 Купить PRO: /buy_pro",
            'batch': f"❌ Пакет более {limit_value} фото доступен только в PRO!\n💰 Купить PRO: /buy_pro",
            'resize': "❌ Изменение размера доступно только в PRO!\n💰 Купить PRO: /buy_pro"
        }
        return messages.get(limit_type, "❌ Функция доступна только в PRO!\n💰 Купить PRO: /buy_pro")


pro_checker = ProChecker()
