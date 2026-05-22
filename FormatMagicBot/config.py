import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 5029334638))

BOT_VERSION = "2.0"
BOT_AUTHOR = "@GdToper"

DONATIONALERTS_URL = "https://www.donationalerts.com/r/magicformatbot"
PRO_PRICE = 99

FREE_QUALITY_MAX = 75
FREE_ICO_MAX = 64
FREE_BATCH_MAX = 3

PRO_QUALITY_MAX = 100
PRO_ICO_MAX = 256
PRO_BATCH_MAX = 50

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_ZIP_SIZE_BYTES = 49 * 1024 * 1024

ALLOWED_FORMATS = ['jpg', 'jpeg', 'png', 'bmp', 'ico', 'webp', 'gif']
QUALITY_OPTIONS = [60, 75, 85, 95, 100]
ICO_SIZE_OPTIONS = [16, 32, 48, 64, 128, 256]
