import os
import logging
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv('config/.env')

# Konfigurasi logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
numeric_level = getattr(logging, log_level.upper(), None)
if not isinstance(numeric_level, int):
    numeric_level = logging.INFO

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=numeric_level
)

logger = logging.getLogger(__name__)

# Memuat konfigurasi dari variabel lingkungan
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN tidak ditemukan. Pastikan Anda menyetelnya di file .env")
    raise ValueError("TELEGRAM_BOT_TOKEN tidak ditemukan")

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY tidak ditemukan. Pastikan Anda menyetelnya di file .env")
    raise ValueError("OPENAI_API_KEY tidak ditemukan")

# ID GPT khusus
GPT_ID = os.getenv('GPT_ID', 'g-67e7e2b2aad0819183cf30988154b9a5')

# Model OpenAI yang digunakan
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')

# Gunakan mode fallback jika terjadi error dengan GPT kustom
USE_FALLBACK = os.getenv('USE_FALLBACK', 'true').lower() == 'true'
logger.info(f"Mode fallback: {'Aktif' if USE_FALLBACK else 'Nonaktif'}")

# Direktori tempat menyimpan gambar sementara
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

# File untuk menyimpan data user
USERS_FILE = os.getenv('USERS_FILE', 'config/users.json')

# Admin ID default (gunakan koma sebagai pemisah jika ada lebih dari satu)
DEFAULT_ADMIN_IDS = os.getenv('DEFAULT_ADMIN_IDS', '')
try:
    DEFAULT_ADMIN_IDS = [int(admin_id.strip()) for admin_id in DEFAULT_ADMIN_IDS.split(',') if admin_id.strip()]
    if DEFAULT_ADMIN_IDS:
        logger.info(f"Default admin IDs: {DEFAULT_ADMIN_IDS}")
    else:
        logger.warning("No default admin IDs configured. Add DEFAULT_ADMIN_IDS in .env file.")
except Exception as e:
    logger.error(f"Error parsing DEFAULT_ADMIN_IDS: {str(e)}")
    DEFAULT_ADMIN_IDS = []

# Nama bot
BOT_NAME = os.getenv('BOT_NAME', 'CryptoScreener AI')

logger.info("Konfigurasi dimuat dengan sukses") 