import os
import base64
import logging
import traceback
import json
import asyncio
from openai import OpenAI
from src.config import OPENAI_API_KEY, GPT_ID, OPENAI_MODEL, USE_FALLBACK
import datetime
import re

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        # Gunakan inisialisasi client yang lebih sederhana
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.gpt_id = GPT_ID
        self.model = OPENAI_MODEL
        self.use_fallback = USE_FALLBACK
        logger.info(f"OpenAI client diinisialisasi dengan model {self.model} dan GPT ID {self.gpt_id}")
        logger.info(f"Mode fallback: {'Aktif' if self.use_fallback else 'Nonaktif'}")
        
        # Verifikasi API key yang digunakan
        logger.debug(f"API key yang digunakan: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-4:]}")
        
        # Cek apakah ini adalah GPT kustom
        self.is_custom_gpt = self.gpt_id.startswith('g-')
        if self.is_custom_gpt:
            logger.info(f"Menggunakan GPT kustom dengan ID: {self.gpt_id}")

    def encode_image(self, image_path):
        """
        Mengubah gambar menjadi base64 string untuk dikirim ke OpenAI
        """
        if not os.path.exists(image_path):
            logger.error(f"File gambar tidak ditemukan: {image_path}")
            raise FileNotFoundError(f"File gambar tidak ditemukan: {image_path}")
        
        try:
            with open(image_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                file_size = os.path.getsize(image_path)
                logger.debug(f"Gambar berhasil di-encode, ukuran file: {file_size/1024:.2f} KB, panjang base64: {len(encoded)} karakter")
                return encoded
        except Exception as e:
            logger.error(f"Error saat mengubah gambar ke base64: {str(e)}")
            raise

    async def analyze_image(self, image_path):
        """
        Mengirim gambar ke GPT khusus dan mendapatkan respons analisis
        """
        try:
            # Encode gambar sebagai base64
            base64_image = self.encode_image(image_path)
            
            logger.info(f"Mengirim gambar untuk dianalisis: {image_path}")
            logger.debug(f"Menggunakan model: {self.gpt_id}, Custom GPT: {self.is_custom_gpt}, Fallback: {self.use_fallback}")
            
            # Pertama coba dengan model standar untuk melihat apakah API key berfungsi
            logger.debug("Verifikasi API key dengan model standar terlebih dahulu")
            try:
                # Test dengan model standar untuk verifikasi API
                test_response = self.client.chat.completions.create(
                    model="gpt-4o",  # Model standar untuk verifikasi
                    messages=[
                        {
                            "role": "user",
                            "content": "Test koneksi API"
                        }
                    ],
                    max_tokens=10
                )
                logger.debug(f"API key valid. Respons test: {test_response.choices[0].message.content}")
            except Exception as e:
                logger.error(f"API key tidak valid atau memiliki masalah: {str(e)}")
                raise ValueError(f"API key tidak valid: {str(e)}")
            
            # Prompt khusus untuk PrimeSwing
            prompt = "Analisis grafik crypto ini dengan timeframe 1 jam. Berikan analisis teknikal lengkap, support/resistance, trend, dan setup entry futures yang optimal dengan target profit dan stop loss. Analisis harus cocok untuk swing trader dengan timeframe H1."
            
            # Log permintaan untuk debugging
            logger.debug(f"Mencoba dengan GPT khusus PrimeSwing. Prompt: {prompt}")
            
            try:
                # Jika menggunakan GPT khusus
                if self.is_custom_gpt:
                    logger.debug(f"API request untuk GPT kustom: model={self.gpt_id}")
                    
                    try:
                        # Mencoba dengan metode standar
                        response = self.client.chat.completions.create(
                            model=self.gpt_id,  # ID GPT khusus
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            max_tokens=1000
                        )
                    except Exception as custom_gpt_error:
                        logger.warning(f"Error dalam menggunakan GPT kustom: {str(custom_gpt_error)}")
                        # Jika mode fallback aktif, gunakan model standar
                        if self.use_fallback:
                            logger.info("Mode fallback aktif, menggunakan model standar")
                            raise custom_gpt_error
                        # Jika mode fallback tidak aktif, teruskan error ke pengguna
                        else:
                            logger.error("Mode fallback tidak aktif, error diteruskan")
                            raise
                else:
                    # Menggunakan model standar
                    response = self.client.chat.completions.create(
                        model=self.model,  # Model standar
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=1000
                    )
            except Exception as e:
                # Error dengan GPT kustom atau model standar
                logger.warning(f"Error dengan model {self.gpt_id}: {str(e)}")
                
                # Jika mode fallback aktif atau bukan error pada GPT kustom
                if self.use_fallback or not self.is_custom_gpt:
                    logger.info(f"Fallback ke model gpt-4o standar")
                    
                    # Fallback ke model standard dengan prompt yang lebih detail
                    response = self.client.chat.completions.create(
                        model="gpt-4o",  # Model standar (gpt-4o)
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Tolong analisis grafik crypto trading ini dengan timeframe 1 jam. Berikan analisis teknikal lengkap termasuk support, resistance, trend, setup entry futures yang optimal, target profit dan stop loss. Fokuskan pada swing trading di timeframe H1."},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=1000
                    )
                else:
                    # Jika mode fallback tidak aktif, teruskan error
                    raise
            
            # Mendapatkan teks respons
            analysis = response.choices[0].message.content
            logger.info("Analisis gambar berhasil diambil dari OpenAI")
            logger.debug(f"Panjang respons: {len(analysis)} karakter")
            
            return analysis
            
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Error detail dalam menganalisis gambar: {str(e)}")
            logger.error(f"Traceback: {error_trace}")
            raise 

    def analyze_photo(self, image_path):
        """
        Versi sinkron untuk menganalisis foto dengan format yang siap untuk Telegram
        """
        try:
            # Encode gambar sebagai base64
            base64_image = self.encode_image(image_path)
            
            logger.info(f"Menganalisis foto: {image_path}")
            
            # Template formatting yang diminta
            format_template = """
Analisis chart crypto berikut dan buat output yang sudah terformat lengkap dengan emoji untuk platform Telegram. Ikuti template format di bawah ini dengan tepat:

🔮 CRYPTOSCREENER AI 🔮

📊 ANALISIS [COIN] [TIMEFRAME] 📊
Symbol: [SYMBOL] | Harga: [CURRENT PRICE]

📈 TREND
- 🚀 TREND UTAMA: [Jelaskan trend utama - uptrend/downtrend/sideways]
- 📊 PERGERAKAN HARGA: [Jelaskan pergerakan harga terkini]

🔍 SUPPORT & RESISTANCE
- 🛡️ SUPPORT KUNCI: [Level support]
- 🔥 RESISTANCE KUNCI: [Level resistance]

⚡ SETUP TRADING
- 💎 POSISI: [LONG/SHORT]
- 🎯 ENTRY: [Harga entry]
- ⏱️ DURASI: [Estimasi waktu pergerakan]

💰 TARGET PROFIT
- 🥉 Target 1: [Harga] (+[Persentase]%)
- 🥈 Target 2: [Harga] (+[Persentase]%)
- 🥇 Target 3: [Harga] (+[Persentase]%)

⛔ STOP LOSS
- 🚨 Stop Loss: [Harga] (-[Persentase]%)

⚖️ RASIO RISK:REWARD
- 📊 R:R = [Rasio]

🧰 SKENARIO LANJUTAN
- ✅ Jika TP tercapai: [Tindakan selanjutnya]
- ❌ Jika SL tercapai: [Tindakan selanjutnya]

<b>⚠️ DISCLAIMER: Bukan saran finansial</b>
<b>🤖 Bot CRYPTOSCREENER AI v1.2</b>

<i>Pastikan untuk selalu melakukan analisis lebih lanjut dan pertimbangan risiko sebelum mengambil keputusan trading.</i>
"""
            
            # Prompt untuk analisis dengan format template yang sudah ditentukan
            prompt = f"""Analisis ini adalah untuk PENDIDIKAN SAJA, tidak mengandung nasihat finansial. 

Analisis pola grafik teknikal dan tampilkan informasi visual yang terlihat pada grafik berikut, menggunakan analisis objektif. Identifikasi pola visual, level harga penting, dan pergerakan historis yang terlihat pada chart. 

Khusus analisis ini, fokus pada TIMEFRAME H1 (1 JAM) yang cocok untuk trading semi-swing dan entry dengan potensi pergerakan jangka menengah. Optimalkan analisis untuk setup futures trading dengan pendekatan PrimeSwing untuk H1.

Berikan output terformat dengan template berikut untuk membantu pembaca memahami apa yang terlihat pada grafik. Perlu diingat analisis ini bersifat pendidikan dan hanya melihat pola visual yang terlihat pada chart.

{format_template}"""
            
            # API request untuk GPT
            try:
                # Mencoba menggunakan GPT kustom jika tersedia
                if self.is_custom_gpt:
                    try:
                        response = self.client.chat.completions.create(
                            model=self.gpt_id,
                            messages=[
                                {
                                    "role": "system",
                                    "content": """Kamu adalah pendidik teknikal analisis yang fokus menganalisis pola visual dan struktur grafik. Tugas utamamu adalah mengidentifikasi dan menjelaskan pola-pola teknikal yang TERLIHAT pada grafik, bukan memberikan rekomendasi atau saran trading. 
                                    
Fokus analisismu pada TIMEFRAME H1 (1 JAM) khusus untuk trading semi-swing dan entry futures dengan durasi menengah. Kamu menggunakan pendekatan PrimeSwing yang mencari entry optimal pada timeframe 1 jam.

Mulai output langsung dengan '🔮 CRYPTOSCREENER AI 🔮' tanpa penjelasan atau disclaimer. Semua analisis adalah untuk tujuan pendidikan dan pemahaman pola grafik saja."""
                                },
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            max_tokens=1500
                        )
                    except Exception as e:
                        logger.warning(f"Error menggunakan GPT kustom: {str(e)}")
                        if not self.use_fallback:
                            raise
                        # Lanjut ke fallback jika diizinkan
                        raise Exception("Menggunakan fallback model")
                else:
                    # Jika tidak menggunakan GPT kustom, langsung gunakan model standar
                    raise Exception("Menggunakan model standar")
                    
            except Exception as e:
                # Fallback ke model standar gpt-4o
                logger.info(f"Menggunakan model fallback: gpt-4o")
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": """Kamu adalah pendidik teknikal analisis yang fokus menganalisis pola visual dan struktur grafik. Tugas utamamu adalah mengidentifikasi dan menjelaskan pola-pola teknikal yang TERLIHAT pada grafik, bukan memberikan rekomendasi atau saran trading. 
                            
Fokus analisismu pada TIMEFRAME H1 (1 JAM) khusus untuk trading semi-swing dan entry futures dengan durasi menengah. Kamu menggunakan pendekatan PrimeSwing yang mencari entry optimal pada timeframe 1 jam.

Mulai output langsung dengan '🔮 CRYPTOSCREENER AI 🔮' tanpa penjelasan atau disclaimer. Semua analisis adalah untuk tujuan pendidikan dan pemahaman pola grafik saja."""
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1500
                )
            
            # Mendapatkan teks respons
            analysis = response.choices[0].message.content
            logger.info("Analisis gambar berhasil diperoleh")
            logger.debug(f"Panjang respons: {len(analysis)} karakter")
            
            # Hapus disclaimer atau text yang tidak diinginkan sebelum template
            if "unable to provide" in analysis.lower() or "i can guide you" in analysis.lower() or "i can't assist" in analysis.lower() or "i'm sorry" in analysis.lower() or "sorry" in analysis.lower():
                match = re.search(r'🔮 CRYPTOSCREENER AI 🔮', analysis)
                if match:
                    start_idx = match.start()
                    analysis = analysis[start_idx:]
                else:
                    # Jika tidak menemukan header CRYPTOSCREENER AI, buat respons fallback sederhana
                    analysis = """🔮 CRYPTOSCREENER AI 🔮

📊 ANALISIS CHART 📊
Symbol: XAU/USD | Harga: Current

📈 TREND
- 🚀 TREND UTAMA: Saat ini tidak dapat dianalisis dengan jelas
- 📊 PERGERAKAN HARGA: Perlu analisis lanjutan

🔍 SUPPORT & RESISTANCE
- 🛡️ SUPPORT KUNCI: Memerlukan analisis lebih detail
- 🔥 RESISTANCE KUNCI: Memerlukan analisis lebih detail

⚡ SETUP TRADING
- 💎 POSISI: Tidak dapat ditentukan
- 🎯 ENTRY: Perlu analisis lanjutan
- ⏱️ DURASI: Tidak dapat diperkirakan

<b>⚠️ DISCLAIMER: Bukan saran finansial</b>
<b>🤖 Bot CRYPTOSCREENER AI v1.2</b>

<i>Pastikan untuk selalu melakukan analisis lebih lanjut dan pertimbangan risiko sebelum mengambil keputusan trading.</i>"""
            
            return analysis
            
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Error dalam analyze_photo: {str(e)}")
            logger.error(f"Traceback: {error_trace}")
            raise 