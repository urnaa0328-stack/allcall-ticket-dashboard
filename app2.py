import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, timedelta, datetime

from ticket_dashboard import render_ticket_dashboard
from sales_dashboard import render_sales_dashboard
from social_dashboard import render_social_dashboard
from operation_dashboard import render_operation_dashboard

st.set_page_config(page_title="AllCall BI Dashboard", page_icon="📊", layout="wide")

# =========================
# BRAND COLORS
# =========================
NAVY = "#02013B"
NAVY_2 = "#060658"
BLUE = "#0D1691"
ACCENT = "#0ACAF9"
WHITE = "#C9CED6"
MUTED = "rgba(241,241,245,0.72)"
CARD_BG = "rgba(255,255,255,0.10)"
CARD_BORDER = "rgba(255,255,255,0.10)"

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent   # app2.py нь dashboard/ дотор байгаа бол root руу 1 алхам дээшилнэ

def resolve_excel_path():
    candidates = [
        PROJECT_ROOT / "data" / "allcall_bi_data.xlsx",   # Documents/allcall-bi-dashboard/data/...
        BASE_DIR / "data" / "allcall_bi_data.xlsx",       # Documents/allcall-bi-dashboard/dashboard/data/...
        PROJECT_ROOT / "allcall_bi_data.xlsx",
        BASE_DIR / "allcall_bi_data.xlsx",
        Path.home() / "Documents" / "allcall_bi_data.xlsx",
    ]

    for p in candidates:
        if p.exists():
            return str(p)

    raise FileNotFoundError(
        "Excel файл олдсонгүй. Checked paths:\n" +
        "\n".join(str(p) for p in candidates)
    )

EXCEL_PATH = resolve_excel_path()

# =========================
# HELPERS
# =========================
def resolve_logo_path() -> str | None:
    candidates = [
        Path("assets/logo.png"),
        Path("logo.png"),
        Path("/mnt/data/logo.png"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None

@st.cache_data(ttl=60)
def load_all_sheets(path: str) -> dict[str, pd.DataFrame]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Excel файл олдсонгүй: {path}")

    xls = pd.ExcelFile(path)
    required = ["Ticket", "Sales", "SocialMedia", "Operation"]

    sheets: dict[str, pd.DataFrame] = {}
    for s in required:
        if s not in xls.sheet_names:
            raise ValueError(f"'{s}' sheet олдсонгүй. Excel sheet names: {xls.sheet_names}")
        sheets[s] = pd.read_excel(xls, sheet_name=s)

    return sheets

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
        padding-top: 1.3rem;
        padding-bottom: 2rem;
    }}

    h1, h2, h3, h4, p, label, div, span {{
        color: {WHITE} !important;
    }}

    section[data-testid="stSidebar"] {{
        background: rgba(1, 3, 45, 0.94);
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
        margin-bottom: 4px;
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
        border-radius: 18px;
        padding: 14px 16px;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 28px rgba(0,0,0,0.18);
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

    .stButton > button,
    .stDownloadButton > button {{
        background: linear-gradient(90deg, {ACCENT}, #68ddff) !important;
        color: {NAVY} !important;
        border: 0 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        background: {BLUE} !important;
        color: {WHITE} !important;
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
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# LOAD DATA
# =========================
try:
    sheets = load_all_sheets(EXCEL_PATH)
except Exception as e:
    st.error(str(e))
    st.stop()

# =========================
# HEADER
# =========================
logo = resolve_logo_path()
h1, h2 = st.columns([1, 3.8], vertical_alignment="center")

with h1:
    if logo:
        st.image(logo, width=150)

with h2:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-badge">📊 <b>AllCall BI Dashboard</b></div>
            <div class="hero-title">Ticket • Sales • Social Media • Operation</div>
            <div class="hero-sub">
                Нэгдсэн удирдлагын тайлангийн самбар
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
    st.markdown("## 📂 Dashboard сонгох")
    menu = st.selectbox(
        "Module",
        ["Overview", "Ticket", "Sales", "SocialMedia", "Operation"],
        index=0,
    )

    st.markdown("---")
    st.markdown("## 📅 Хугацаа")
    today = date.today()
    dfrom = st.date_input("Эхлэх огноо", value=today - timedelta(days=29))
    dto = st.date_input("Дуусах огноо", value=today)

    st.markdown("---")
    st.markdown(f"<div class='mini-note'>Файл: <b>{EXCEL_PATH}</b></div>", unsafe_allow_html=True)

# =========================
# OVERVIEW
# =========================
if menu == "Overview":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("Executive Overview")

    ticket_df = sheets["Ticket"].copy()
    sales_df = sheets["Sales"].copy()
    social_df = sheets["SocialMedia"].copy()
    operation_df = sheets["Operation"].copy()

    # Simple summary KPIs
    total_tickets = len(ticket_df)
    resolved_tickets = int((ticket_df.get("status", pd.Series(dtype=str)).astype(str) == "Шийдвэрлэсэн").sum()) if "status" in ticket_df.columns else 0

    total_leads = len(sales_df)
    won_leads = int((sales_df.get("won_flag", pd.Series(dtype=float)).fillna(0).astype(float) == 1).sum()) if "won_flag" in sales_df.columns else 0

    total_social_spend = float(pd.to_numeric(social_df.get("total_spend_mnt", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "total_spend_mnt" in social_df.columns else 0.0

    total_tasks = len(operation_df)
    done_tasks = int((operation_df.get("completion_flag", pd.Series(dtype=float)).fillna(0).astype(float) == 1).sum()) if "completion_flag" in operation_df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Нийт тикет", f"{total_tickets:,}")
    c2.metric("Won sales", f"{won_leads:,}", f"/ {total_leads:,}")
    c3.metric("Social spend", f"₮{total_social_spend:,.0f}")
    c4.metric("Дууссан ажил", f"{done_tasks:,}", f"/ {total_tasks:,}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.info("Sidebar-аас module сонгоод дэлгэрэнгүй dashboard руу орно уу.")

elif menu == "Ticket":
    render_ticket_dashboard(sheets["Ticket"], dfrom, dto, ACCENT)

elif menu == "Sales":
    render_sales_dashboard(sheets["Sales"], dfrom, dto, ACCENT)

elif menu == "SocialMedia":
    render_social_dashboard(sheets["SocialMedia"], dfrom, dto, ACCENT)

elif menu == "Operation":
    render_operation_dashboard(sheets["Operation"], dfrom, dto, ACCENT)
