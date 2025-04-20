# UltraScalp Bot Telegram

Bot Telegram untuk menganalisis grafik trading menggunakan UltraScalp GPT.

## Deskripsi

Bot ini memungkinkan pengguna untuk mengirim gambar grafik trading melalui Telegram, yang kemudian diteruskan ke GPT khusus UltraScalp untuk analisis mendalam. Hasil analisis akan dikirim kembali ke pengguna Telegram.

## Fitur

- Menerima gambar dari pengguna Telegram
- Mengirimkan gambar ke UltraScalp GPT untuk analisis
- Mengembalikan hasil analisis ke pengguna
- Penanganan error yang baik
- Logging untuk debugging

## Persiapan

1. Dapatkan API key Telegram Bot melalui [BotFather](https://t.me/botfather)
2. Dapatkan API key OpenAI
3. Siapkan file konfigurasi

## Instalasi

1. Pastikan Python 3.8+ terinstal
2. Salin file `.env.example` di direktori `config` menjadi `.env`
3. Perbarui `.env` dengan API key Telegram Bot dan OpenAI Anda
4. Instal dependensi yang diperlukan:

```bash
pip install -r requirements.txt
```

## Penggunaan

Untuk menjalankan bot:

```bash
python main.py
```

### Perintah Bot

- `/start` - Memulai bot
- `/help` - Menampilkan bantuan

### Cara Menggunakan

1. Mulai chat dengan bot Anda di Telegram
2. Kirim gambar grafik trading yang ingin dianalisis
3. Bot akan memproses gambar dan mengirimkan ke UltraScalp GPT
4. Tunggu respons dengan analisis yang akan dikirim kembali ke Anda

## Struktur Proyek

```
├── config/             # Konfigurasi aplikasi
│   └── .env.example    # Contoh file konfigurasi
├── src/                # Kode sumber
│   ├── __init__.py
│   ├── config.py       # Konfigurasi dan environment
│   ├── openai_client.py  # Integrasi dengan OpenAI
│   └── telegram_bot.py # Implementasi bot Telegram
├── temp/               # Direktori untuk file sementara
├── main.py             # Entrypoint aplikasi
├── README.md           # Dokumentasi
└── requirements.txt    # Dependensi
```

## Catatan Penting

- Bot ini menggunakan GPT khusus dengan ID `g-67e7e2b2aad0819183cf30988154b9a5`
- Penggunaan gambar dikenakan biaya API sesuai dengan harga OpenAI
- Disarankan menggunakan model `gpt-4o` untuk hasil terbaik atau `gpt-4o-mini` untuk biaya lebih rendah

## Troubleshooting

Jika Anda mengalami masalah:

- Pastikan API key Telegram Bot dan OpenAI valid
- Periksa log untuk detail error
- Pastikan bot memiliki akses untuk mengirim dan menerima pesan 