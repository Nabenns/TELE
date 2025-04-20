# CryptoScreener AI - H1 Timeframe

Bot Telegram untuk menganalisis gambar grafik trading crypto secara otomatis menggunakan AI, khusus untuk timeframe H1 (1 jam).

## Fitur

- 🔍 **Analisis Teknikal Otomatis**: Unggah grafik trading dan dapatkan analisis lengkap
- 📊 **Detail Analisis**: Support/resistance, trend, entry points, target profit, dan stop loss
- 🕐 **Timeframe H1**: Analisis khusus untuk grafik 1 jam, ideal untuk swing trading
- 🔐 **Sistem Whitelist**: Hanya pengguna yang diizinkan yang dapat mengakses bot
- 👑 **Manajemen Admin**: Tambah/hapus pengguna yang diizinkan melalui perintah admin
- 🖼️ **Dukungan Format**: Analisis grafik dalam format gambar (JPG, PNG)
- 🧠 **AI Bertenaga**: Menggunakan GPT "Futures Maximizer: PrimeSwing" yang dioptimalkan untuk analisis timeframe 1 jam

## Persyaratan

- Python 3.8+
- Telegram Bot token (dari [BotFather](https://t.me/botfather))
- API key OpenAI

## Instalasi

1. Clone repositori ini:
   ```bash
   git clone https://github.com/yourusername/cryptoscreener-ai-h1.git
   cd cryptoscreener-ai-h1
   ```

2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```

3. Salin file konfigurasi contoh:
   ```bash
   cp config/.env.example config/.env
   ```

4. Edit file `config/.env` dan isi dengan kredensial Anda:
   - `TELEGRAM_BOT_TOKEN`: Token bot Telegram Anda
   - `OPENAI_API_KEY`: API key OpenAI Anda
   - `DEFAULT_ADMIN_IDS`: ID Telegram Anda untuk akses admin (pisahkan dengan koma jika lebih dari satu)

## Penggunaan

1. Jalankan bot:
   ```bash
   python main.py
   ```

2. Di Telegram, mulai percakapan dengan bot Anda.

3. Gunakan perintah `/start` untuk memulai dan `/help` untuk melihat bantuan.

4. Kirim gambar grafik trading untuk mendapatkan analisis.

## Perintah Admin

- `/admin` - Menampilkan panel admin
- `/adduser [user_id]` - Menambahkan pengguna ke daftar yang diizinkan
- `/removeuser [user_id]` - Menghapus pengguna dari daftar yang diizinkan
- `/listusers` - Menampilkan daftar admin dan pengguna yang diizinkan

## Sistem Whitelist

Bot ini menggunakan sistem whitelist untuk membatasi akses hanya kepada pengguna yang diizinkan:

1. **Admin**: Memiliki akses penuh ke bot dan dapat mengelola pengguna lain
2. **Pengguna yang Diizinkan**: Dapat menggunakan bot untuk menganalisis gambar

Saat pertama kali menjalankan bot, Anda perlu menambahkan ID Telegram Anda sebagai admin di file `.env`:
```
DEFAULT_ADMIN_IDS=your_telegram_id_here
```

Kemudian Anda dapat menambahkan pengguna lain menggunakan perintah `/adduser`.

## Cara Mendapatkan ID Telegram

Untuk mendapatkan ID Telegram Anda atau pengguna lain:

1. Mulai percakapan dengan [@userinfobot](https://t.me/userinfobot) di Telegram
2. Bot akan mengirimkan ID Anda
3. Untuk mendapatkan ID pengguna lain, minta mereka melakukan hal yang sama

## Pengembangan

### Struktur Proyek

```
.
├── config/             # File konfigurasi
│   └── .env            # Variabel lingkungan
├── src/                # Kode sumber
│   ├── config.py       # Konfigurasi
│   ├── openai_client.py # Klien OpenAI
│   ├── telegram_bot.py # Bot Telegram
│   └── user_manager.py # Pengelola pengguna
├── temp/               # Direktori sementara untuk gambar
├── main.py             # File utama
└── requirements.txt    # Dependensi
```

## Lisensi

MIT

## Kontribusi

Kontribusi sangat diterima! Silakan buka issue atau pull request untuk perbaikan atau fitur baru. 