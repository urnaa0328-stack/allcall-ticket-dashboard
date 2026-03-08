import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
from datetime import datetime, timedelta, date

st.set_page_config(page_title="AllCall ticket Dashboard", page_icon="📊", layout="wide")

# =========================
# BRAND COLORS
# =========================
NAVY = "#02013B"
NAVY_2 = "#060658"
BLUE = "#0D1691"
ACCENT = "#0ACAF9"
WHITE = "#C9CED6"
MUTED = "rgba(241,241,245,0.72)"
CARD_BG = "rgba(255,255,255,0.12)"
CARD_BORDER = "rgba(255,255,255,0.12)"

# =========================
# LOGO + FILE PATH
# =========================
DEFAULT_XLSX = "complains.xlsx"
SHEET_NAME = "Report"

def resolve_logo_path() -> str | None:
    candidates = [
        Path("assets/logo.png"),
        Path.home() / "Documents" / "logo.png",
        Path("/mnt/data/logo.png"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None

# =========================
# CSS
# =========================
st.markdown(
    f"""
    <style>
    .stApp {{
        background:
            radial-gradient(900px 500px at 88% 20%, rgba(13,22,145,.45) 0%, rgba(2,1,59,0) 60%),
            linear-gradient(135deg, {NAVY} 0%, {NAVY_2} 42%, {BLUE} 100%);
        color: {WHITE};
    }}

    .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }}

    h1, h2, h3, h4, p, label, div, span {{
        color: {WHITE} !important;
    }}

    section[data-testid="stSidebar"] {{
        background: rgba(1, 3, 45, 0.92);
        border-right: 1px solid rgba(255,255,255,0.08);
    }}

    .hero {{
        background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(10,202,249,0.05));
        border: 1px solid rgba(10,202,249,0.18);
        border-radius: 22px;
        padding: 18px 20px;
        box-shadow: 0 16px 40px rgba(0,0,0,0.25);
        backdrop-filter: blur(10px);
    }}

    .hero-title {{
        font-size: 1.8rem;
        font-weight: 900;
        letter-spacing: .2px;
        margin-bottom: 2px;
    }}

    .hero-sub {{
        color: {MUTED} !important;
        font-size: .95rem;
    }}

    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(10,202,249,0.12);
        border: 1px solid rgba(10,202,249,0.22);
        font-size: 0.85rem;
        margin-bottom: 10px;
    }}

    .glass {{
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 20px;
        padding: 16px 16px;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 28px rgba(0,0,0,0.22);
    }}

    .section-title {{
        font-size: 1.08rem;
        font-weight: 800;
        margin-bottom: 10px;
    }}

    .kpi-card {{
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 18px;
        padding: 15px 16px;
        min-height: 120px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    }}

    .kpi-top {{
        display:flex;
        justify-content:space-between;
        align-items:center;
        margin-bottom:8px;
    }}

    .kpi-title {{
        font-size:.92rem;
        color:{MUTED} !important;
        font-weight:600;
    }}

    .kpi-icon {{
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display:flex;
        align-items:center;
        justify-content:center;
        background: rgba(10,202,249,0.14);
        border: 1px solid rgba(10,202,249,0.24);
        font-size: 1rem;
    }}

    .kpi-value {{
        font-size: 2rem;
        font-weight: 900;
        line-height: 1.1;
    }}

    .kpi-sub {{
        margin-top: 5px;
        font-size: .84rem;
        color: {MUTED} !important;
    }}

    .mini-note {{
        color: {MUTED} !important;
        font-size: .88rem;
    }}

    .divider {{
        height: 1px;
        background: rgba(255,255,255,0.10);
        margin: 14px 0 18px 0;
    }}

    .stButton > button {{
        background: linear-gradient(90deg, {ACCENT}, #68ddff) !important;
        color: {NAVY} !important;
        border: 0 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
    }}

    .stButton > button:hover {{
        background: {BLUE} !important;
        color: {WHITE} !important;
    }}

    .stDownloadButton > button {{
        background: linear-gradient(90deg, {ACCENT}, #68ddff) !important;
        color: {NAVY} !important;
        border: 0 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
    }}

    div[data-baseweb="select"] > div,
    .stDateInput > div > div,
    .stTextInput > div > div > input {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: {WHITE} !important;
        border-radius: 12px !important;
    }}

    [data-testid="stDataFrame"] {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        overflow: hidden;
    }}

    .footer {{
        text-align:center;
        color:{MUTED} !important;
        margin-top:20px;
        font-size:.88rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS
# =========================
@st.cache_data(ttl=60)
def load_excel(path: str, sheet_name: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Excel файл олдсонгүй: {path}")
    return pd.read_excel(path, sheet_name=sheet_name)

def norm_str(x) -> str:
    return "" if pd.isna(x) else str(x).strip()

def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    dfx = df.copy()
    dfx["Огноо"] = pd.to_datetime(dfx["Огноо"], errors="coerce")

    for col in ["Суваг", "Төрөл", "Санал, гомдол", "Төлөв", "Оператор"]:
        if col in dfx.columns:
            dfx[col] = dfx[col].apply(norm_str)
    return dfx

def get_period_df(df: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
    return df[(df["Огноо"] >= start_dt) & (df["Огноо"] < end_dt)].copy()

def compute_kpi(df: pd.DataFrame, repeat_basis: str = "Төрөл") -> dict:
    total = len(df)

    status_counts = df["Төлөв"].value_counts().to_dict()
    resolved = int(status_counts.get("Шийдвэрлэсэн", 0))
    accepted = int(status_counts.get("Хүлээн авсан", 0))
    transferred = int(status_counts.get("Шилжүүлсэн", 0))
    checking = int(status_counts.get("Шалгаж байгаа", 0))

    repeat_col = "Төрөл" if repeat_basis == "Төрөл" else "Санал, гомдол"
    rep = df[repeat_col].dropna().astype(str).str.strip()
    rep = rep[rep != ""]
    rep_counts = rep.value_counts()

    top_repeat = rep_counts.index[0] if len(rep_counts) else "—"
    top_repeat_count = int(rep_counts.iloc[0]) if len(rep_counts) else 0

    rep_top10 = rep_counts.head(10).reset_index()
    rep_top10.columns = ["item", "count"]

    resolved_df = df[df["Төлөв"] == "Шийдвэрлэсэн"].copy()
    op_counts = resolved_df["Оператор"].value_counts()

    top_operator = op_counts.index[0] if len(op_counts) else "—"
    top_operator_count = int(op_counts.iloc[0]) if len(op_counts) else 0

    op_top10 = op_counts.head(10).reset_index()
    op_top10.columns = ["operator", "resolved_count"]

    trend = df.copy()
    trend["date_only"] = trend["Огноо"].dt.date
    trend_daily = trend.groupby("date_only").size().reset_index(name="count")

    status_trend = (
        trend.groupby(["date_only", "Төлөв"])
        .size()
        .reset_index(name="count")
    )

    channel_counts = (
        df["Суваг"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    channel_counts = channel_counts[channel_counts != ""]
    channel_counts = channel_counts.value_counts().reset_index()
    channel_counts.columns = ["channel", "count"]

    top_channel = channel_counts.iloc[0]["channel"] if not channel_counts.empty else "—"
    top_channel_count = int(channel_counts.iloc[0]["count"]) if not channel_counts.empty else 0

    return {
        "total": total,
        "resolved": resolved,
        "accepted": accepted,
        "transferred": transferred,
        "checking": checking,
        "top_repeat": top_repeat,
        "top_repeat_count": top_repeat_count,
        "rep_top10": rep_top10,
        "top_operator": top_operator,
        "top_operator_count": top_operator_count,
        "op_top10": op_top10,
        "trend_daily": trend_daily,
        "status_trend": status_trend,
        "status_counts": status_counts,
        "channel_counts": channel_counts,
        "top_channel": top_channel,
        "top_channel_count": top_channel_count,
    }

def compare_value(current: int, previous: int) -> str:
    diff = current - previous
    sign = "+" if diff > 0 else ""
    return f"{sign}{diff}"

def render_kpi_card(title: str, value: str, subtitle: str, icon: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <div class="kpi-title">{title}</div>
                <div class="kpi-icon">{icon}</div>
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# HEADER
# =========================
logo = resolve_logo_path()
h1, h2 = st.columns([1, 3.6], vertical_alignment="center")

with h1:
    if logo:
        st.image(logo, width=150)

with h2:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-badge">📊 <b>AllCall KPI Dashboard</b></div>
            <div class="hero-title">Тикетын тайлан</div>
            <div class="hero-sub">
                Статус хяналт • Давтагдсан асуудал • Хамгийн олон тикет шийдвэрлэсэн инженер • Суваг бүрийн хуваарилалт
            </div>
            <div class="hero-sub" style="margin-top:6px;">
                🕒 Сүүлд шинэчлэгдсэн: <b>{datetime.now().strftime("%Y-%m-%d %H:%M")}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Тохиргоо")
    file_path = st.text_input("Excel file path", value=DEFAULT_XLSX)
    repeat_basis = st.radio(
        "Давтагдсан асуудлыг юугаар бодох вэ?",
        ["Төрөл", "Санал, гомдол"],
        index=0
    )

    st.markdown("---")
    st.markdown("## 📅 Хугацаа")
    today = date.today()
    default_from = today - timedelta(days=6)

    dfrom = st.date_input("Эхлэх огноо", value=default_from)
    dto = st.date_input("Дуусах огноо", value=today)

# =========================
# LOAD DATA
# =========================
try:
    raw_df = load_excel(file_path, SHEET_NAME)
    df = prepare_df(raw_df)
except Exception as e:
    st.error(str(e))
    st.stop()

required_cols = ["Огноо", "Суваг", "Төрөл", "Санал, гомдол", "Төлөв", "Оператор"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Дараах баганууд олдсонгүй: {', '.join(missing)}")
    st.stop()

# =========================
# CURRENT / PREVIOUS PERIOD
# =========================
current_df = get_period_df(df, dfrom, dto)

days = (dto - dfrom).days + 1
prev_to = dfrom - timedelta(days=1)
prev_from = prev_to - timedelta(days=days - 1)
previous_df = get_period_df(df, prev_from, prev_to)

cur = compute_kpi(current_df, repeat_basis=repeat_basis)
prev = compute_kpi(previous_df, repeat_basis=repeat_basis)

# =========================
# KPI SECTION
# =========================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown(f'<div class="section-title">7 хоногийн KPI ({dfrom} → {dto})</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Шийдвэрлэсэн", f"{cur['resolved']:,}", f"Өмнөхөөс {compare_value(cur['resolved'], prev['resolved'])}", "✅")
with c2:
    render_kpi_card("Хүлээн авсан", f"{cur['accepted']:,}", f"Өмнөхөөс {compare_value(cur['accepted'], prev['accepted'])}", "📥")
with c3:
    render_kpi_card("Шалгаж байгаа", f"{cur['checking']:,}", f"Өмнөхөөс {compare_value(cur['checking'], prev['checking'])}", "🔍")
with c4:
    render_kpi_card("Шилжүүлсэн", f"{cur['transferred']:,}", f"Өмнөхөөс {compare_value(cur['transferred'], prev['transferred'])}", "🔁")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)
with c5:
    render_kpi_card("Нийт асуудал", f"{cur['total']:,}", f"Өмнөхөөс {compare_value(cur['total'], prev['total'])}", "📊")
with c6:
    render_kpi_card("Хамгийн олон давтагдсан асуудал", f"{cur['top_repeat_count']:,}", f"{cur['top_repeat']}", "🧩")
with c7:
    render_kpi_card("Хамгийн олон тикет шийдсэн инженер", f"{cur['top_operator_count']:,}", f"{cur['top_operator']}", "🏆")
with c8:
    render_kpi_card("Top суваг", f"{cur['top_channel_count']:,}", f"{cur['top_channel']}", "📡")

st.markdown(
    f"<div class='mini-note'>Өмнөх харьцуулах хугацаа: <b>{prev_from}</b> → <b>{prev_to}</b></div>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =========================
# CHARTS
# =========================
left, right = st.columns(2)

with left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Суваг тус бүрээр бүртгэгдсэн тикетийн тоо</div>', unsafe_allow_html=True)

    if cur["channel_counts"].empty:
        st.info("Энэ хугацаанд дата алга.")
    else:
        ch = alt.Chart(cur["channel_counts"]).mark_bar(
            color=ACCENT,
            cornerRadiusEnd=6
        ).encode(
            y=alt.Y("channel:N", sort="-x", title="Суваг"),
            x=alt.X("count:Q", title="Тоо"),
            tooltip=["channel:N", "count:Q"]
        ).properties(height=300)

        st.altair_chart(ch, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Статусын өдөр тутмын хуваарилалт</div>', unsafe_allow_html=True)
    if cur["status_trend"].empty:
        st.info("Энэ хугацаанд дата алга.")
    else:
        status_order = ["Шийдвэрлэсэн", "Хүлээн авсан", "Шалгаж байгаа", "Шилжүүлсэн"]
        color_scale = alt.Scale(
            domain=status_order,
            range=[ACCENT, "#56B4FF", "#7D8CFF", "#AEB4C5"]
        )

        ch2 = alt.Chart(cur["status_trend"]).mark_bar().encode(
            x=alt.X("date_only:T", title="Огноо"),
            y=alt.Y("count:Q", title="Тоо"),
            color=alt.Color("Төлөв:N", title="Төлөв", scale=color_scale),
            tooltip=["date_only:T", "Төлөв:N", "count:Q"]
        ).properties(height=300)
        st.altair_chart(ch2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =========================
# TOP 10
# =========================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔁 Хамгийн олон давтагдсан асуудал (Top 10)</div>', unsafe_allow_html=True)
    if cur["rep_top10"].empty:
        st.info("Дата алга")
    else:
        bar1 = alt.Chart(cur["rep_top10"]).mark_bar(
            color=ACCENT,
            cornerRadiusEnd=6
        ).encode(
            y=alt.Y("item:N", sort="-x", title=""),
            x=alt.X("count:Q", title="Тоо"),
            tooltip=["item:N", "count:Q"]
        ).properties(height=320)
        st.altair_chart(bar1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏆 Хамгийн олон тикет шийдвэрлэсэн ажилтан (Top 10)</div>', unsafe_allow_html=True)
    if cur["op_top10"].empty:
        st.info("Дата алга")
    else:
        bar2 = alt.Chart(cur["op_top10"]).mark_bar(
            color="#56B4FF",
            cornerRadiusEnd=6
        ).encode(
            y=alt.Y("operator:N", sort="-x", title=""),
            x=alt.X("resolved_count:Q", title="Шийдсэн тоо"),
            tooltip=["operator:N", "resolved_count:Q"]
        ).properties(height=320)
        st.altair_chart(bar2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =========================
# RAW DATA
# =========================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 Дэлгэрэнгүй жагсаалт</div>', unsafe_allow_html=True)
st.dataframe(current_df, use_container_width=True, height=400)

csv = current_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ CSV татах",
    csv,
    file_name="complain_kpi_filtered.csv",
    mime="text/csv"
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer">
        © AllCall • Incredible service • Incredible business
    </div>
    """,
    unsafe_allow_html=True,
)
