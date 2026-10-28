"""
FinReport ID - Dashboard Laporan Keuangan Perusahaan Publik
Sumber data: Yahoo Finance (via pustaka yfinance)

Jalankan:  streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ---------------------------------------------------------------------------
# Konfigurasi halaman
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FinReport ID | Laporan Keuangan Emiten",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1400px;}

:root {
  --navy: #0b2545;
  --blue: #13315c;
  --accent: #1d6fdc;
  --muted: #5b6b82;
  --border: #e3e8ef;
  --bg-soft: #f5f7fb;
}

.hero {
  background: linear-gradient(120deg, #0b2545 0%, #13315c 55%, #1d6fdc 120%);
  color: #fff; padding: 22px 28px; border-radius: 14px; margin-bottom: 18px;
}
.hero h1 {margin: 0; font-size: 1.7rem; font-weight: 700; letter-spacing: .2px; color:#fff;}
.hero p {margin: 4px 0 0 0; color: #cfdcf2; font-size: .95rem;}

.company-card {
  background: #fff; border: 1px solid var(--border); border-radius: 14px;
  padding: 18px 22px; margin-bottom: 14px;
  box-shadow: 0 1px 2px rgba(16,24,40,.04);
}
.company-card .name {font-size: 1.35rem; font-weight: 700; color: var(--navy);}
.company-card .ticker {
  display:inline-block; background:#e8f0fe; color: var(--accent); font-weight:600;
  padding: 2px 10px; border-radius: 999px; font-size: .8rem; margin-left: 8px;
}
.company-card .meta {color: var(--muted); font-size: .88rem; margin-top: 4px;}
.chips {margin-top: 10px;}
.chip {
  display:inline-block; background: var(--bg-soft); border:1px solid var(--border);
  color: var(--navy); padding: 4px 12px; border-radius: 8px; font-size: .82rem; margin: 0 8px 6px 0;
}
.chip b {color: var(--blue);}

div[data-testid="stMetric"] {
  background: #fff; border: 1px solid var(--border); border-radius: 12px;
  padding: 14px 16px; box-shadow: 0 1px 2px rgba(16,24,40,.04);
}
div[data-testid="stMetricLabel"] {color: var(--muted);}

button[data-baseweb="tab"] {font-weight: 600; font-size: 1rem; padding: 10px 18px;}
.section-title {font-size: 1.05rem; font-weight: 700; color: var(--navy); margin: 6px 0 2px 0;}
.note {color: var(--muted); font-size: .82rem;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Konstanta & kamus label
# ---------------------------------------------------------------------------
UNITS = {"Penuh": 1.0, "Ribu": 1e3, "Juta": 1e6, "Miliar": 1e9, "Triliun": 1e12}
QUICK_PICKS = ["BBCA", "BBRI", "BMRI", "TLKM", "ASII", "GOTO"]
NO_SCALE_KEYWORDS = ("EPS", "Shares", "Share Issued", "Tax Rate", "Number")

ID_LABELS = {
    # Laba rugi
    "Total Revenue": "Total Pendapatan",
    "Operating Revenue": "Pendapatan Operasional",
    "Cost Of Revenue": "Beban Pokok Pendapatan",
    "Gross Profit": "Laba Kotor",
    "Operating Expense": "Beban Operasional",
    "Selling General And Administrative": "Beban Penjualan, Umum & Administrasi",
    "General And Administrative Expense": "Beban Umum & Administrasi",
    "Selling And Marketing Expense": "Beban Penjualan & Pemasaran",
    "Research And Development": "Penelitian & Pengembangan",
    "Operating Income": "Laba Operasional",
    "Net Non Operating Interest Income Expense": "Pendapatan (Beban) Bunga Neto Non-Operasional",
    "Interest Income": "Pendapatan Bunga",
    "Interest Expense": "Beban Bunga",
    "Other Income Expense": "Pendapatan (Beban) Lain-lain",
    "Pretax Income": "Laba Sebelum Pajak",
    "Tax Provision": "Beban Pajak",
    "Tax Rate For Calcs": "Tarif Pajak",
    "Net Income": "Laba Bersih",
    "Net Income Common Stockholders": "Laba Bersih Pemegang Saham Biasa",
    "Net Income Continuous Operations": "Laba Bersih Operasi Berlanjut",
    "Net Income From Continuing Operation Net Minority Interest": "Laba Bersih Operasi Berlanjut (Setelah KNP)",
    "Minority Interests": "Kepentingan Non-Pengendali",
    "Basic EPS": "EPS Dasar",
    "Diluted EPS": "EPS Dilusian",
    "Basic Average Shares": "Rata-rata Saham Dasar",
    "Diluted Average Shares": "Rata-rata Saham Dilusian",
    "Total Expenses": "Total Beban",
    "Normalized Income": "Laba Normalisasi",
    "Normalized EBITDA": "EBITDA Normalisasi",
    "Depreciation And Amortization In Income Statement": "Penyusutan & Amortisasi",
    # Neraca
    "Total Assets": "Total Aset",
    "Current Assets": "Aset Lancar",
    "Cash Cash Equivalents And Short Term Investments": "Kas, Setara Kas & Investasi Jangka Pendek",
    "Cash And Cash Equivalents": "Kas & Setara Kas",
    "Cash Financial": "Kas",
    "Other Short Term Investments": "Investasi Jangka Pendek Lainnya",
    "Receivables": "Piutang",
    "Accounts Receivable": "Piutang Usaha",
    "Inventory": "Persediaan",
    "Prepaid Assets": "Biaya Dibayar di Muka",
    "Other Current Assets": "Aset Lancar Lainnya",
    "Total Non Current Assets": "Total Aset Tidak Lancar",
    "Net PPE": "Aset Tetap Neto",
    "Goodwill": "Goodwill",
    "Other Intangible Assets": "Aset Tak Berwujud Lainnya",
    "Investments And Advances": "Investasi & Uang Muka",
    "Long Term Equity Investment": "Investasi Ekuitas Jangka Panjang",
    "Other Non Current Assets": "Aset Tidak Lancar Lainnya",
    "Total Liabilities Net Minority Interest": "Total Liabilitas",
    "Current Liabilities": "Liabilitas Jangka Pendek",
    "Payables": "Utang",
    "Accounts Payable": "Utang Usaha",
    "Current Debt": "Utang Jangka Pendek",
    "Current Deferred Revenue": "Pendapatan Diterima di Muka (Lancar)",
    "Other Current Liabilities": "Liabilitas Jangka Pendek Lainnya",
    "Total Non Current Liabilities Net Minority Interest": "Total Liabilitas Jangka Panjang",
    "Long Term Debt": "Utang Jangka Panjang",
    "Long Term Debt And Capital Lease Obligation": "Utang Jangka Panjang & Sewa",
    "Other Non Current Liabilities": "Liabilitas Jangka Panjang Lainnya",
    "Total Debt": "Total Utang",
    "Net Debt": "Utang Neto",
    "Stockholders Equity": "Ekuitas Pemegang Saham",
    "Common Stock Equity": "Ekuitas Saham Biasa",
    "Total Equity Gross Minority Interest": "Total Ekuitas",
    "Minority Interest": "Kepentingan Non-Pengendali",
    "Capital Stock": "Modal Saham",
    "Common Stock": "Saham Biasa",
    "Additional Paid In Capital": "Tambahan Modal Disetor",
    "Retained Earnings": "Saldo Laba",
    "Working Capital": "Modal Kerja",
    "Invested Capital": "Modal Investasi",
    "Tangible Book Value": "Nilai Buku Berwujud",
    "Ordinary Shares Number": "Jumlah Saham Beredar",
    "Share Issued": "Saham Diterbitkan",
    "Total Capitalization": "Total Kapitalisasi",
    "Net Tangible Assets": "Aset Berwujud Neto",
    # Arus kas
    "Operating Cash Flow": "Arus Kas dari Aktivitas Operasi",
    "Investing Cash Flow": "Arus Kas dari Aktivitas Investasi",
    "Financing Cash Flow": "Arus Kas dari Aktivitas Pendanaan",
    "Free Cash Flow": "Arus Kas Bebas",
    "Capital Expenditure": "Belanja Modal (Capex)",
    "Changes In Cash": "Perubahan Kas Neto",
    "Beginning Cash Position": "Kas Awal Periode",
    "End Cash Position": "Kas Akhir Periode",
    "Depreciation And Amortization": "Penyusutan & Amortisasi",
    "Depreciation Amortization Depletion": "Penyusutan, Amortisasi & Deplesi",
    "Change In Working Capital": "Perubahan Modal Kerja",
    "Stock Based Compensation": "Kompensasi Berbasis Saham",
    "Deferred Income Tax": "Pajak Penghasilan Tangguhan",
    "Issuance Of Debt": "Penerbitan Utang",
    "Repayment Of Debt": "Pembayaran Utang",
    "Cash Dividends Paid": "Dividen Tunai Dibayar",
    "Common Stock Dividend Paid": "Dividen Saham Biasa Dibayar",
    "Repurchase Of Capital Stock": "Pembelian Kembali Saham",
    "Issuance Of Capital Stock": "Penerbitan Saham",
    "Purchase Of PPE": "Pembelian Aset Tetap",
    "Sale Of PPE": "Penjualan Aset Tetap",
    "Purchase Of Investment": "Pembelian Investasi",
    "Sale Of Investment": "Penjualan Investasi",
    "Interest Paid Supplemental Data": "Bunga Dibayar",
    "Income Tax Paid Supplemental Data": "Pajak Penghasilan Dibayar",
    "Net Income From Continuing Operations": "Laba Bersih dari Operasi Berlanjut",
}

# Baris total / subtotal yang disorot di tabel.
KEY_ROWS = {
    "Total Revenue", "Gross Profit", "Operating Income", "Pretax Income",
    "Net Income", "Net Income Common Stockholders", "EBITDA", "EBIT",
    "Total Assets", "Current Assets", "Total Non Current Assets",
    "Total Liabilities Net Minority Interest", "Current Liabilities",
    "Total Non Current Liabilities Net Minority Interest",
    "Stockholders Equity", "Total Equity Gross Minority Interest",
    "Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow",
    "Free Cash Flow", "End Cash Position",
}

DEFAULT_CHART_ROWS = {
    "income": ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"],
    "balance": ["Total Assets", "Total Liabilities Net Minority Interest", "Stockholders Equity"],
    "cashflow": ["Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow", "Free Cash Flow"],
}


# ---------------------------------------------------------------------------
# Fungsi bantu
# ---------------------------------------------------------------------------
def normalize_symbol(raw: str, market: str) -> str:
    sym = (raw or "").strip().upper().replace(" ", "")
    if not sym:
        return ""
    if market.startswith("Indonesia") and "." not in sym and not sym.startswith("^"):
        sym += ".JK"
    return sym


def clean_statement(df: pd.DataFrame | None) -> pd.DataFrame:
    """Rapikan DataFrame laporan: buang baris kosong, urutkan kolom terbaru -> lama."""
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    out = out.dropna(how="all")
    try:
        out.columns = pd.to_datetime(out.columns)
        out = out.reindex(sorted(out.columns, reverse=True), axis=1)
    except Exception:
        pass
    return out


@st.cache_data(ttl=3600, show_spinner=False)
def load_data(symbol: str, period: str) -> dict:
    t = yf.Ticker(symbol)
    if period == "Tahunan":
        inc, bal, cf = t.income_stmt, t.balance_sheet, t.cashflow
    else:
        inc, bal, cf = t.quarterly_income_stmt, t.quarterly_balance_sheet, t.quarterly_cashflow
    try:
        info = t.info or {}
    except Exception:
        info = {}
    return {
        "income": clean_statement(inc),
        "balance": clean_statement(bal),
        "cashflow": clean_statement(cf),
        "info": info,
    }


def fmt_cell(v) -> str:
    if v is None or pd.isna(v):
        return "–"
    a = abs(v)
    s = f"{a:,.0f}" if a >= 1000 else f"{a:,.2f}"
    return f"({s})" if v < 0 else s


def fmt_compact(v, currency: str | None) -> str:
    if v is None or pd.isna(v):
        return "–"
    if currency == "IDR":
        units = [(1e12, "T"), (1e9, "M"), (1e6, "Jt")]
        prefix = "Rp "
    else:
        units = [(1e12, "T"), (1e9, "B"), (1e6, "M")]
        prefix = "" if not currency else f"{currency} "
    a = abs(v)
    sign = "-" if v < 0 else ""
    for div, suf in units:
        if a >= div:
            return f"{sign}{prefix}{a / div:,.2f} {suf}"
    return f"{sign}{prefix}{a:,.0f}"


def period_label(ts, period: str) -> str:
    try:
        ts = pd.Timestamp(ts)
    except Exception:
        return str(ts)
    if period == "Tahunan":
        return f"FY {ts.year}  ({ts.strftime('%d %b %Y')})"
    q = (ts.month - 1) // 3 + 1
    return f"Q{q} {ts.year}  ({ts.strftime('%d %b %Y')})"


def latest_and_delta(df: pd.DataFrame, row: str):
    """Nilai terbaru dan perubahan (%) dibanding periode sebelumnya."""
    if df.empty or row not in df.index:
        return None, None
    s = df.loc[row].dropna()
    if s.empty:
        return None, None
    cur = s.iloc[0]
    delta = None
    if len(s) > 1 and s.iloc[1] not in (0, None) and not pd.isna(s.iloc[1]):
        delta = (cur - s.iloc[1]) / abs(s.iloc[1]) * 100
    return cur, delta


def show_df(obj, height: int):
    try:
        st.dataframe(obj, height=height, width="stretch")
    except TypeError:
        st.dataframe(obj, height=height, use_container_width=True)


def show_plot(fig):
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def render_statement(df: pd.DataFrame, kind: str, scale_name: str, lang: str,
                     period: str, symbol: str):
    if df.empty:
        st.warning("Data untuk laporan ini tidak tersedia di sumber data.")
        return

    divisor = UNITS[scale_name]
    work = df.copy()

    # Skala nilai (kecuali EPS, jumlah saham, tarif pajak)
    scalable = [not any(k in str(i) for k in NO_SCALE_KEYWORDS) for i in work.index]
    work.loc[scalable] = work.loc[scalable] / divisor

    # Label akun
    en_index = list(work.index)
    if lang == "Indonesia":
        labels = [ID_LABELS.get(i, i) for i in en_index]
    else:
        labels = en_index
    work.index = labels
    work.index.name = "Akun" if lang == "Indonesia" else "Account"
    work.columns = [period_label(c, period) for c in work.columns]

    key_labels = {
        (ID_LABELS.get(i, i) if lang == "Indonesia" else i)
        for i in en_index if i in KEY_ROWS
    }

    # Pencarian baris
    q = st.text_input(
        "Cari akun",
        key=f"filter_{kind}",
        placeholder="mis. pendapatan, aset, dividen ...",
        label_visibility="collapsed",
    )
    view = work
    if q:
        view = work[work.index.str.contains(q, case=False, regex=False)]
        if view.empty:
            st.info("Tidak ada akun yang cocok dengan pencarian.")

    def style_rows(row):
        if row.name in key_labels:
            return ["font-weight: 700; background-color: #eef3fb; color: #0b2545"] * len(row)
        return [""] * len(row)

    if not view.empty:
        styled = view.style.format(fmt_cell).apply(style_rows, axis=1)
        height = int(min(36 * (len(view) + 1) + 4, 720))
        show_df(styled, height)

    unit_note = "nilai penuh" if divisor == 1 else f"dalam {scale_name.lower()}"
    st.markdown(
        f'<div class="note">Angka {unit_note} (kecuali EPS & jumlah saham). '
        f"Angka dalam kurung = negatif. Baris tebal = total/subtotal. "
        f"Gulir ke kanan untuk periode sebelumnya.</div>",
        unsafe_allow_html=True,
    )

    st.download_button(
        "⬇ Unduh CSV",
        data=work.to_csv().encode("utf-8-sig"),
        file_name=f"{symbol}_{kind}_{'annual' if period == 'Tahunan' else 'quarterly'}.csv",
        mime="text/csv",
        key=f"dl_{kind}",
    )

    # Grafik tren
    with st.expander("Grafik tren akun", expanded=True):
        defaults = [
            (ID_LABELS.get(i, i) if lang == "Indonesia" else i)
            for i in DEFAULT_CHART_ROWS[kind] if i in en_index
        ]
        picks = st.multiselect(
            "Pilih akun untuk grafik",
            options=list(work.index),
            default=defaults,
            key=f"chart_{kind}",
        )
        if picks:
            # urutan waktu naik (lama -> baru)
            cols_asc = list(work.columns)[::-1]
            fig = go.Figure()
            for p in picks:
                fig.add_bar(
                    name=p,
                    x=[c.split("  ")[0] for c in cols_asc],
                    y=[work.loc[p, c] for c in cols_asc],
                )
            fig.update_layout(
                barmode="group",
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", y=-0.2),
                yaxis_title=f"Nilai ({scale_name})",
                template="plotly_white",
            )
            show_plot(fig)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
if "symbol_input" not in st.session_state:
    st.session_state.symbol_input = "BBCA"


def set_symbol(s: str):
    st.session_state.symbol_input = s


with st.sidebar:
    st.markdown("### 🔎 Cari Emiten")
    market = st.selectbox(
        "Pasar",
        ["Indonesia (IDX, .JK)", "Global (AS & lainnya)"],
        help="Pasar Indonesia otomatis menambahkan akhiran .JK (BBCA → BBCA.JK). "
             "Pilih Global untuk kode seperti AAPL, MSFT, 7203.T, dll.",
    )
    st.text_input(
        "Kode saham",
        key="symbol_input",
        placeholder="mis. BBCA, TLKM, AAPL",
        help="Tekan Enter untuk memuat data.",
    )
    period = st.radio("Periode laporan", ["Tahunan", "Kuartalan"], horizontal=True)

    st.markdown("**Pilihan cepat (IDX)**")
    cols = st.columns(3)
    for i, s in enumerate(QUICK_PICKS):
        cols[i % 3].button(s, key=f"qp_{s}", on_click=set_symbol, args=(s,))

    st.divider()
    st.markdown("### ⚙ Tampilan")
    default_unit = 3 if market.startswith("Indonesia") else 2  # Miliar / Juta
    scale_name = st.selectbox("Satuan angka", list(UNITS.keys()), index=default_unit)
    lang = st.radio("Label akun", ["Indonesia", "English"], horizontal=True)

    st.divider()
    st.caption(
        "Sumber data: Yahoo Finance via yfinance. Data bersifat informatif dan "
        "dapat tertunda/tidak lengkap; verifikasi dengan laporan resmi emiten "
        "(IDX / OJK) sebelum mengambil keputusan investasi."
    )

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <h1>📊 FinReport ID</h1>
      <p>Laporan keuangan perusahaan publik — Laba Rugi, Neraca, dan Arus Kas dalam satu dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

symbol = normalize_symbol(st.session_state.symbol_input, market)
if not symbol:
    st.info("Masukkan kode saham di sidebar untuk memulai (contoh: BBCA, TLKM, AAPL).")
    st.stop()

# ---------------------------------------------------------------------------
# Muat data
# ---------------------------------------------------------------------------
try:
    with st.spinner(f"Memuat laporan keuangan {symbol} ..."):
        data = load_data(symbol, period)
except Exception as exc:  # jaringan, rate limit, dll.
    st.error(
        f"Gagal mengambil data untuk **{symbol}**. Kemungkinan koneksi bermasalah atau "
        f"Yahoo Finance membatasi permintaan. Coba lagi beberapa saat.\n\nDetail: `{exc}`"
    )
    st.stop()

inc, bal, cf, info = data["income"], data["balance"], data["cashflow"], data["info"]

if inc.empty and bal.empty and cf.empty:
    st.error(
        f"Tidak ada data laporan keuangan untuk **{symbol}**. Periksa kembali kode saham "
        f"dan pilihan pasar (Indonesia memakai akhiran .JK, mis. BBCA.JK)."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Profil perusahaan
# ---------------------------------------------------------------------------
fin_ccy = info.get("financialCurrency") or info.get("currency")
name = info.get("longName") or info.get("shortName") or symbol
meta_bits = [b for b in [info.get("sector"), info.get("industry"), info.get("exchange")] if b]

chips = []
price = info.get("currentPrice") or info.get("regularMarketPrice")
if price is not None:
    chips.append(f"Harga <b>{price:,.2f} {info.get('currency', '')}</b>")
if info.get("marketCap"):
    chips.append(f"Kapitalisasi pasar <b>{fmt_compact(info['marketCap'], info.get('currency'))}</b>")
if info.get("trailingPE"):
    chips.append(f"P/E <b>{info['trailingPE']:.2f}</b>")
if info.get("priceToBook"):
    chips.append(f"P/B <b>{info['priceToBook']:.2f}</b>")
if info.get("dividendYield"):
    dy = info["dividendYield"]
    dy = dy if dy > 1 else dy * 100  # yfinance kadang dalam persen, kadang desimal
    chips.append(f"Dividend yield <b>{dy:.2f}%</b>")
if fin_ccy:
    chips.append(f"Mata uang laporan <b>{fin_ccy}</b>")

website = info.get("website")
st.markdown(
    f"""
    <div class="company-card">
      <span class="name">{name}</span><span class="ticker">{symbol}</span>
      <div class="meta">{' · '.join(meta_bits) if meta_bits else '—'}
        {(' · <a href="' + website + '" target="_blank">' + website + '</a>') if website else ''}</div>
      <div class="chips">{''.join(f'<span class="chip">{c}</span>' for c in chips)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
if info.get("longBusinessSummary"):
    with st.expander("Profil bisnis"):
        st.write(info["longBusinessSummary"])

# ---------------------------------------------------------------------------
# Ringkasan metrik
# ---------------------------------------------------------------------------
latest_ref = None
for d in (inc, bal, cf):
    if not d.empty:
        latest_ref = d.columns[0]
        break
if latest_ref is not None:
    st.caption(f"Periode terbaru: **{period_label(latest_ref, period)}** · "
               f"perubahan dibandingkan periode sebelumnya")

metric_defs = [
    ("Total Pendapatan", inc, "Total Revenue"),
    ("Laba Bersih", inc, "Net Income"),
    ("Total Aset", bal, "Total Assets"),
    ("Arus Kas Operasi", cf, "Operating Cash Flow"),
]
mcols = st.columns(4)
for col, (label, frame, row) in zip(mcols, metric_defs):
    val, delta = latest_and_delta(frame, row)
    col.metric(label, fmt_compact(val, fin_ccy),
               None if delta is None else f"{delta:+.1f}%")

st.write("")

# ---------------------------------------------------------------------------
# Tiga laporan keuangan
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Laporan Laba Rugi", "Laporan Posisi Keuangan (Neraca)", "Laporan Arus Kas"])

with tab1:
    st.markdown('<div class="section-title">Laporan Laba Rugi (Income Statement)</div>',
                unsafe_allow_html=True)
    render_statement(inc, "income", scale_name, lang, period, symbol)

with tab2:
    st.markdown('<div class="section-title">Laporan Posisi Keuangan (Balance Sheet)</div>',
                unsafe_allow_html=True)
    render_statement(bal, "balance", scale_name, lang, period, symbol)

with tab3:
    st.markdown('<div class="section-title">Laporan Arus Kas (Cash Flow Statement)</div>',
                unsafe_allow_html=True)
    render_statement(cf, "cashflow", scale_name, lang, period, symbol)

if period == "Kuartalan":
    st.caption("Catatan: Yahoo Finance umumnya hanya menyediakan sekitar 4–5 kuartal terakhir; "
               "emiten IDX tertentu bisa memiliki data kuartalan yang terbatas.")
