import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date

def _prepare_sales_df(df: pd.DataFrame) -> pd.DataFrame:
    dfx = df.copy()
    if "date" in dfx.columns:
        dfx["date"] = pd.to_datetime(dfx["date"], errors="coerce")
    return dfx

def _filter_period(df: pd.DataFrame, dfrom: date, dto: date) -> pd.DataFrame:
    if "date" not in df.columns:
        return df.copy()
    start_dt = datetime.combine(dfrom, datetime.min.time())
    end_dt = datetime.combine(dto + timedelta(days=1), datetime.min.time())
    return df[(df["date"] >= start_dt) & (df["date"] < end_dt)].copy()

def render_sales_dashboard(df: pd.DataFrame, dfrom: date, dto: date, accent: str):
    st.subheader("💼 Sales Dashboard")

    dfx = _prepare_sales_df(df)
    cur = _filter_period(dfx, dfrom, dto)

    total_leads = len(cur)
    won = int(pd.to_numeric(cur.get("won_flag", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "won_flag" in cur.columns else 0
    lost = int(pd.to_numeric(cur.get("lost_flag", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "lost_flag" in cur.columns else 0
    total_pipeline = float(pd.to_numeric(cur.get("deal_value", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "deal_value" in cur.columns else 0.0
    weighted_pipeline = float(pd.to_numeric(cur.get("weighted_value", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "weighted_value" in cur.columns else 0.0
    win_rate = (won / (won + lost) * 100) if (won + lost) else 0.0

    stage_df = pd.DataFrame(columns=["stage", "count"])
    if "stage" in cur.columns:
        vc = cur["stage"].dropna().astype(str).str.strip().value_counts()
        stage_df = vc.reset_index()
        stage_df.columns = ["stage", "count"]

    owner_df = pd.DataFrame(columns=["owner", "count"])
    if "owner" in cur.columns:
        vc = cur["owner"].dropna().astype(str).str.strip().value_counts().head(10)
        owner_df = vc.reset_index()
        owner_df.columns = ["owner", "count"]

    source_df = pd.DataFrame(columns=["source", "count"])
    if "source" in cur.columns:
        vc = cur["source"].dropna().astype(str).str.strip().value_counts()
        source_df = vc.reset_index()
        source_df.columns = ["source", "count"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Нийт lead", f"{total_leads:,}")
    c2.metric("Won", f"{won:,}")
    c3.metric("Lost", f"{lost:,}")
    c4.metric("Win rate", f"{win_rate:.1f}%")

    c5, c6 = st.columns(2)
    c5.metric("Нийт pipeline", f"₮{total_pipeline:,.0f}")
    c6.metric("Weighted pipeline", f"₮{weighted_pipeline:,.0f}")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.markdown("#### 📊 Stage distribution")
        if stage_df.empty:
            st.info("Дата алга")
        else:
            ch = alt.Chart(stage_df).mark_bar(color=accent, cornerRadiusEnd=6).encode(
                y=alt.Y("stage:N", sort="-x", title=""),
                x=alt.X("count:Q", title="Тоо"),
                tooltip=["stage:N", "count:Q"]
            ).properties(height=300)
            st.altair_chart(ch, use_container_width=True)

    with right:
        st.markdown("#### 📡 Lead source distribution")
        if source_df.empty:
            st.info("Дата алга")
        else:
            ch = alt.Chart(source_df).mark_arc(innerRadius=60).encode(
                theta="count:Q",
                color=alt.Color("source:N", title="Source"),
                tooltip=["source:N", "count:Q"]
            ).properties(height=300)
            st.altair_chart(ch, use_container_width=True)

    st.divider()
    st.markdown("#### 🏆 Top owners")
    if owner_df.empty:
        st.info("Дата алга")
    else:
        bar = alt.Chart(owner_df).mark_bar(color="#56B4FF", cornerRadiusEnd=6).encode(
            y=alt.Y("owner:N", sort="-x", title=""),
            x=alt.X("count:Q", title="Lead count"),
            tooltip=["owner:N", "count:Q"]
        ).properties(height=320)
        st.altair_chart(bar, use_container_width=True)

    st.divider()
    st.markdown("#### 📋 Дэлгэрэнгүй жагсаалт")
    st.dataframe(cur, use_container_width=True, height=360)