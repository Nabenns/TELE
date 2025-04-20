import os
import uuid
import logging
import traceback
import re
import datetime
import time
import functools
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from src.config import TELEGRAM_BOT_TOKEN, TEMP_DIR, DEFAULT_ADMIN_IDS, BOT_NAME, USERS_FILE
from src.openai_client import OpenAIClient
from src.user_manager import UserManager
import openai

logger = logging.getLogger(__name__)

def access_control(admin_only=False):
    """
    Dekorator untuk memeriksa akses pengguna ke bot
    
    Args:
        admin_only: Apakah fitur hanya untuk admin
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            
            # Cek apakah user diizinkan
            if admin_only and not self.user_manager.is_admin(user_id):
                await update.message.reply_text(
                    "⛔ Maaf, fitur ini hanya tersedia untuk admin.",
                    parse_mode=ParseMode.HTML
                )
                logger.warning(f"User {user_id} mencoba mengakses fitur admin")
                return
            
            if not self.user_manager.is_allowed(user_id):
                await update.message.reply_text(
                    f"⛔ <b>Akses Ditolak</b>\n\n"
                    f"Maaf, Anda tidak memiliki akses ke {BOT_NAME}.\n\n"
                    f"Silakan hubungi admin untuk mendapatkan akses.",
                    parse_mode=ParseMode.HTML
                )
                logger.warning(f"User {user_id} ditolak aksesnya")
                return
            
            # Jalankan fungsi asli
            return await func(self, update, context, *args, **kwargs)
        return wrapper
    return decorator

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.openai_client = OpenAIClient()
        self.user_manager = UserManager(USERS_FILE)
        
        # Tambahkan admin default dari konfigurasi
        for admin_id in DEFAULT_ADMIN_IDS:
            self.user_manager.add_admin(admin_id)
        
        logger.info(f"{BOT_NAME} bot diinisialisasi")
        
        # Tambahkan handler
        self._add_handlers()
    
    def _add_handlers(self):
        """Menambahkan handler untuk perintah dan pesan"""
        # Handler untuk perintah /start
        self.application.add_handler(CommandHandler("start", self.start_command))
        
        # Handler untuk perintah /help
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Handler untuk perintah admin
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("adduser", self.add_user_command))
        self.application.add_handler(CommandHandler("removeuser", self.remove_user_command))
        self.application.add_handler(CommandHandler("listusers", self.list_users_command))
        
        # Handler untuk gambar
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Handler untuk pesan teks
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        logger.info("Handler bot Telegram ditambahkan")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /start"""
        user = update.effective_user
        user_id = user.id
        
        # Cek apakah user diizinkan
        if not self.user_manager.is_allowed(user_id):
            await update.message.reply_text(
                f"👋 Halo {user.first_name}!\n\n"
                f"Maaf, Anda belum memiliki akses ke {BOT_NAME}.\n"
                f"Silakan hubungi admin untuk mendapatkan akses.",
                parse_mode=ParseMode.HTML
            )
            logger.info(f"User {user_id} mencoba memulai bot tapi tidak memiliki akses")
            return
        
        await update.message.reply_text(
            f"Halo {user.first_name}! 👋\n\n"
            f"Selamat datang di {BOT_NAME}! Saya adalah bot yang akan membantu menganalisis grafik trading crypto.\n\n"
            f"Cukup kirimkan gambar grafik trading Anda, dan saya akan memberikan analisis lengkap.\n\n"
            f"Ketik /help untuk informasi lebih lanjut."
        )
        logger.info(f"User {user.id} memulai bot")
    
    @access_control()
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /help"""
        user = update.effective_user
        is_admin = self.user_manager.is_admin(user.id)
        
        help_text = (
            f"<b>🔍 PANDUAN PENGGUNAAN {BOT_NAME}</b>\n\n"
            "<b>Langkah-langkah:</b>\n"
            "1️⃣ Kirim gambar grafik trading crypto untuk dianalisis\n"
            "2️⃣ Pastikan grafik dalam timeframe 1 jam untuk hasil optimal\n"
            "3️⃣ Bot akan menganalisis gambar dengan AI\n"
            "4️⃣ Tunggu beberapa saat untuk menerima hasil analisis\n\n"
            "<b>Analisis akan mencakup:</b>\n"
            "• <b>Support & Resistance</b> - Level kunci untuk pergerakan harga\n"
            "• <b>Trend Direction</b> - Arah pergerakan market\n"
            "• <b>Entry Points</b> - Rekomendasi titik masuk posisi\n"
            "• <b>Take Profit & Stop Loss</b> - Level manajemen risiko\n\n"
            "<b>Perintah yang tersedia:</b>\n"
            "/start - Memulai bot\n"
            "/help - Menampilkan bantuan ini"
        )
        
        # Tambahkan perintah admin jika user adalah admin
        if is_admin:
            help_text += "\n\n<b>Perintah Admin:</b>\n"
            help_text += "/admin - Panel admin\n"
            help_text += "/adduser [user_id] - Tambahkan user\n"
            help_text += "/removeuser [user_id] - Hapus user\n"
            help_text += "/listusers - Lihat daftar user"
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
        logger.info(f"User {update.effective_user.id} meminta bantuan")
    
    @access_control(admin_only=True)
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /admin"""
        help_text = (
            "<b>🔧 PANEL ADMIN</b>\n\n"
            "<b>Perintah yang tersedia:</b>\n"
            "/adduser [user_id] - Tambahkan user\n"
            "/removeuser [user_id] - Hapus user\n"
            "/listusers - Lihat daftar user\n\n"
            "<b>Contoh:</b>\n"
            "/adduser 123456789 - Tambahkan user dengan ID 123456789\n"
            "/removeuser 123456789 - Hapus user dengan ID 123456789"
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
        logger.info(f"User {update.effective_user.id} mengakses panel admin")
    
    @access_control(admin_only=True)
    async def add_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /adduser"""
        # Dapatkan argumen perintah
        args = context.args
        if not args or not args[0].isdigit():
            await update.message.reply_text(
                "❌ <b>Error:</b> Format yang benar adalah /adduser [user_id]",
                parse_mode=ParseMode.HTML
            )
            return
        
        user_id = int(args[0])
        # Tambahkan user
        if self.user_manager.add_allowed_user(user_id):
            await update.message.reply_text(
                f"✅ <b>Berhasil:</b> User ID {user_id} ditambahkan ke daftar yang diizinkan",
                parse_mode=ParseMode.HTML
            )
            logger.info(f"Admin {update.effective_user.id} menambahkan user {user_id}")
        else:
            await update.message.reply_text(
                f"ℹ️ <b>Info:</b> User ID {user_id} sudah ada dalam daftar yang diizinkan",
                parse_mode=ParseMode.HTML
            )
    
    @access_control(admin_only=True)
    async def remove_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /removeuser"""
        # Dapatkan argumen perintah
        args = context.args
        if not args or not args[0].isdigit():
            await update.message.reply_text(
                "❌ <b>Error:</b> Format yang benar adalah /removeuser [user_id]",
                parse_mode=ParseMode.HTML
            )
            return
        
        user_id = int(args[0])
        # Cek apakah user adalah admin yang mencoba menghapus dirinya sendiri
        if user_id == update.effective_user.id and self.user_manager.is_admin(user_id):
            await update.message.reply_text(
                "❌ <b>Error:</b> Anda tidak dapat menghapus diri sendiri dari daftar admin",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Hapus user
        if self.user_manager.remove_allowed_user(user_id):
            await update.message.reply_text(
                f"✅ <b>Berhasil:</b> User ID {user_id} dihapus dari daftar yang diizinkan",
                parse_mode=ParseMode.HTML
            )
            logger.info(f"Admin {update.effective_user.id} menghapus user {user_id}")
        else:
            await update.message.reply_text(
                f"ℹ️ <b>Info:</b> User ID {user_id} tidak ditemukan dalam daftar yang diizinkan",
                parse_mode=ParseMode.HTML
            )
    
    @access_control(admin_only=True)
    async def list_users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /listusers"""
        admins = self.user_manager.get_admins()
        allowed_users = self.user_manager.get_allowed_users()
        
        message = "<b>👥 DAFTAR PENGGUNA</b>\n\n"
        
        if admins:
            message += "<b>Admin:</b>\n"
            for admin_id in admins:
                message += f"🔑 {admin_id}\n"
        else:
            message += "<b>Admin:</b> Tidak ada\n"
        
        message += "\n"
        
        if allowed_users:
            message += "<b>Pengguna yang Diizinkan:</b>\n"
            for user_id in allowed_users:
                message += f"👤 {user_id}\n"
        else:
            message += "<b>Pengguna yang Diizinkan:</b> Tidak ada\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        logger.info(f"Admin {update.effective_user.id} melihat daftar pengguna")
    
    def format_analysis_html(self, analysis_text):
        try:
            # Extract symbol if available
            symbol_match = re.search(r'Symbol:\s*(.+?)(?:\n|$)', analysis_text)
            symbol = symbol_match.group(1) if symbol_match else "Unknown"
            
            # Extract timeframe if available
            timeframe_match = re.search(r'Timeframe:\s*(.+?)(?:\n|$)', analysis_text)
            timeframe = timeframe_match.group(1) if timeframe_match else "Unknown"
            
            # Convert markdown **text** to HTML bold tags
            main_text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', analysis_text)
            
            # Convert markdown ### headers to HTML bold tags
            main_text = re.sub(r'###\s+([^\n]+)', r'<b>\1</b>', main_text)
            
            # Split into sections
            sections = main_text.split('\n\n')
            
            # Format the header
            header = f"🔎 <b>ANALISIS {symbol} ({timeframe})</b> 🔍"
            
            # Format the rest of the analysis with proper HTML tags
            formatted_sections = []
            
            for section in sections:
                if "Tren" in section:
                    section = section.replace("Tren:", "<b>📈 Tren:</b>")
                elif "Potensi Entry Points" in section:
                    section = section.replace("Potensi Entry Points:", "<b>🎯 Potensi Entry Points:</b>")
                elif "Support dan Resistance" in section:
                    section = section.replace("Support dan Resistance:", "<b>📊 Support dan Resistance:</b>")
                    # Add bullet points to support and resistance levels
                    section = section.replace("Support:", "• <b>Support:</b>")
                    section = section.replace("Resistance:", "• <b>Resistance:</b>")
                elif "Target" in section:
                    section = section.replace("Target:", "<b>🏆 Target:</b>")
                elif "Stop Loss" in section:
                    section = section.replace("Stop Loss:", "<b>🛑 Stop Loss:</b>")
                    
                formatted_sections.append(section)
            
            # Join the formatted sections
            body = "\n\n".join(formatted_sections)
            
            # Add a footer
            footer = f"\n\n<i>💡 Pesan ini dibuat oleh {BOT_NAME}. Selalu gunakan judgement Anda sendiri dalam trading.</i>"
            
            # Combine all parts
            return f"{header}\n\n{body}{footer}"
        except Exception as e:
            logging.error(f"Error formatting analysis as HTML: {e}")
            return analysis_text  # Return original text if formatting fails

    def format_simple_analysis_html(self, analysis_text):
        try:
            # Extract basic information
            symbol_match = re.search(r'Symbol:\s*(.+?)(?:\n|$)', analysis_text)
            symbol = symbol_match.group(1) if symbol_match else "Unknown"
            
            timeframe_match = re.search(r'Timeframe:\s*(.+?)(?:\n|$)', analysis_text)
            timeframe = timeframe_match.group(1) if timeframe_match else "Unknown"
            
            # Create a clean header
            header = f"📊 <b>ANALISIS {symbol} ({timeframe})</b>"
            
            # Look for trend indicators and format with emojis
            trend_match = re.search(r'(?:Tren|Trend)[^:]*:\s*(.+?)(?:\n|$)', analysis_text, re.IGNORECASE)
            trend_text = ""
            if trend_match:
                trend = trend_match.group(1).lower()
                if "naik" in trend or "bullish" in trend or "up" in trend:
                    trend_text = f"<b>Trend:</b> 📈 {trend_match.group(1)}"
                elif "turun" in trend or "bearish" in trend or "down" in trend:
                    trend_text = f"<b>Trend:</b> 📉 {trend_match.group(1)}"
                else:
                    trend_text = f"<b>Trend:</b> ↔️ {trend_match.group(1)}"
            
            # Format support and resistance
            support_match = re.search(r'Support:?\s*(.+?)(?:\n|$|\s*Resistance)', analysis_text)
            support_text = ""
            if support_match:
                support_text = f"<b>Support:</b> 🟢 {support_match.group(1)}"
            
            resistance_match = re.search(r'Resistance:?\s*(.+?)(?:\n|$)', analysis_text)
            resistance_text = ""
            if resistance_match:
                resistance_text = f"<b>Resistance:</b> 🔴 {resistance_match.group(1)}"
            
            # Extract entry points
            entry_match = re.search(r'(?:Entry|Potensi Entry Points)[^:]*:\s*(.+?)(?:\n\n|$)', analysis_text, re.DOTALL)
            entry_text = ""
            if entry_match:
                entry = entry_match.group(1)
                # Color code buy/sell entries
                entry = re.sub(r'(Buy|Beli)[^:]*:?\s*(.+?)(?:\n|$)', r'<b>Beli:</b> 💚 \2', entry, flags=re.IGNORECASE)
                entry = re.sub(r'(Sell|Jual)[^:]*:?\s*(.+?)(?:\n|$)', r'<b>Jual:</b> ❤️ \2', entry, flags=re.IGNORECASE)
                entry_text = f"<b>Entry Points:</b>\n{entry}"
            
            # Extract targets and stop loss
            target_match = re.search(r'Target[^:]*:\s*(.+?)(?:\n\n|$)', analysis_text, re.DOTALL)
            target_text = ""
            if target_match:
                target_text = f"<b>Target:</b> 🎯 {target_match.group(1)}"
            
            stop_loss_match = re.search(r'Stop Loss[^:]*:\s*(.+?)(?:\n\n|$)', analysis_text, re.DOTALL)
            stop_loss_text = ""
            if stop_loss_match:
                stop_loss_text = f"<b>Stop Loss:</b> 🛑 {stop_loss_match.group(1)}"
            
            # Assemble the formatted text
            sections = [
                header,
                trend_text,
                support_text,
                resistance_text,
                entry_text,
                target_text,
                stop_loss_text
            ]
            
            # Filter out empty sections
            formatted_text = "\n\n".join([s for s in sections if s])
            
            # Add a footer
            footer = f"\n\n<i>💡 Analisis oleh {BOT_NAME}</i>"
            
            return f"{formatted_text}{footer}"
        except Exception as e:
            logging.error(f"Error in simple HTML formatting: {e}")
            return analysis_text  # Return original text if formatting fails
    
    @access_control()
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming photos."""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        try:
            # Send a "Processing..." message
            processing_message = await context.bot.send_message(
                chat_id=chat_id,
                text="⏳ <b>Sedang memproses chart...</b>",
                parse_mode=ParseMode.HTML
            )
            
            # Get the photo file
            photo_file = await update.message.photo[-1].get_file()
            file_path = os.path.join("temp", f"image_{time.time()}.jpg")
            await photo_file.download_to_drive(file_path)
            
            logging.info(f"Downloaded photo from user {user_id} to {file_path}")
            
            # Analyze the photo - the formatting is now done in the OpenAI client
            analysis = self.openai_client.analyze_photo(file_path)
            
            # Try to delete the file
            try:
                os.remove(file_path)
                logging.info(f"Deleted temporary file {file_path}")
            except Exception as e:
                logging.warning(f"Could not delete temporary file {file_path}: {e}")
            
            # Send the response directly - already formatted appropriately
            await context.bot.send_message(
                chat_id=chat_id,
                text=analysis,
                parse_mode=ParseMode.HTML
            )
            
            # Delete the "Processing..." message
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=processing_message.message_id
            )
            
            logger.info(f"Successfully processed photo from user {user_id}")
            
        except Exception as e:
            logging.error(f"Error handling photo from user {user_id}: {e}")
            traceback_str = traceback.format_exc()
            logging.error(f"Traceback: {traceback_str}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ <b>Error:</b> Terjadi kesalahan saat memproses foto. Silakan coba lagi nanti.",
                parse_mode=ParseMode.HTML
            )
    
    @access_control()
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk pesan teks selain perintah"""
        await update.message.reply_text(
            f"📈 <b>Silakan kirim gambar grafik trading crypto untuk mendapatkan analisis.</b>\n"
            f"Ketik /help untuk bantuan.",
            parse_mode=ParseMode.HTML
        )
    
    def run(self):
        """Menjalankan bot (metode sinkron untuk dijalankan)"""
        logger.info(f"{BOT_NAME} mulai berjalan")
        logger.info(f"Bot berjalan, tekan Ctrl+C untuk berhenti")
        
        # Jalankan bot secara non-async (lebih sederhana untuk Windows)
        self.application.run_polling() 