#!/usr/bin/env python3
"""
Bot Telegram untuk menganalisis gambar grafik trading dengan UltraScalp GPT
"""

import os
import logging
from src.config import TEMP_DIR
from src.telegram_bot import TelegramBot

# Pastikan direktori sementara ada
os.makedirs(TEMP_DIR, exist_ok=True)

# Setup logging
logger = logging.getLogger(__name__)

def main():
    """
    Fungsi utama untuk menjalankan bot
    """
    try:
        logger.info("Memulai bot UltraScalp...")
        bot = TelegramBot()
        
        # Jalankan bot
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot dihentikan oleh pengguna")
    except Exception as e:
        logger.error(f"Error tidak terduga: {str(e)}")
        raise
    finally:
        logger.info("Bot selesai")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program dihentikan oleh pengguna")
    except Exception as e:
        print(f"Error fatal: {str(e)}")
        raise 