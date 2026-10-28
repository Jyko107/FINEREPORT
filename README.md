# FinReport ID — Dashboard Laporan Keuangan Emiten

Dashboard interaktif (Streamlit + yfinance) untuk melihat Laporan Laba Rugi, Neraca, dan Arus Kas
perusahaan publik Indonesia (IDX, akhiran `.JK`) maupun saham global.

## Menjalankan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Buka http://localhost:8501.

## Fitur

- Pencarian kode saham (pasar Indonesia otomatis menambah `.JK`; pilih "Global" untuk AAPL, MSFT, dll.)
- Periode Tahunan / Kuartalan
- 3 tab: Laba Rugi, Neraca, Arus Kas — tabel interaktif (sortir, scroll vertikal/horizontal, kolom akun tetap terlihat)
- Pencarian baris akun, unduh CSV, grafik tren akun
- Satuan angka (Penuh/Ribu/Juta/Miliar/Triliun) dan label akun Indonesia/English
- Kartu ringkasan: pendapatan, laba bersih, total aset, arus kas operasi + perubahan vs periode sebelumnya

## Catatan

- Data berasal dari Yahoo Finance dan bisa tertunda, tidak lengkap, atau berbeda dari laporan resmi emiten.
  Gunakan laporan resmi di idx.co.id untuk keputusan investasi.
- Hasil di-cache 1 jam. Jika terkena rate limit Yahoo, tunggu beberapa menit lalu coba lagi.
- Data kuartalan Yahoo biasanya hanya ±4–5 kuartal terakhir.
