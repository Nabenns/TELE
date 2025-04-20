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

logger.info("Konfigurasi dimuat dengan sukses") 