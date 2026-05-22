from io import BytesIO
import zipfile
from datetime import datetime
from services.converter import convert_image


class BatchManager:
    def __init__(self):
        self.batches = {}

    def add_image(self, user_id, file_bytes, file_format):
        if user_id not in self.batches:
            self.batches[user_id] = {'images': [], 'formats': []}
        self.batches[user_id]['images'].append(file_bytes)
        self.batches[user_id]['formats'].append(file_format)

    def get_batch(self, user_id):
        return self.batches.get(user_id, {'images': [], 'formats': []})

    def clear_batch(self, user_id):
        if user_id in self.batches:
            self.batches[user_id] = {'images': [], 'formats': []}

    async def convert_batch(self, user_id, target_format, quality, ico_size):
        batch = self.get_batch(user_id)
        if not batch['images']:
            return None

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for idx, img_bytes in enumerate(batch['images']):
                converted = await convert_image(img_bytes, target_format, quality, ico_size)
                ext = target_format.lower()
                if ext == "jpeg":
                    ext = "jpg"
                zf.writestr(f"image_{idx+1}.{ext}", converted)

        zip_buffer.seek(0)
        self.clear_batch(user_id)
        return zip_buffer.getvalue()


batch_manager = BatchManager()
