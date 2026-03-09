import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date

def _norm_str(x) -> str:
    return "" if pd.isna(x) else str(x).strip()

def _prepare_ticket_df(df: pd.DataFrame) -> pd.DataFrame:
    dfx = df.copy()

    if "date" in dfx.columns:
        dfx["date"] = pd.to_datetime(dfx["date"], errors="coerce")

    for col in ["channel", "issue_type", "issue_detail", "status", "operator_name"]:
        if col in dfx.columns:
            dfx[col] = dfx[col].apply(_norm_str)

    return dfx

def _filter_period(df: pd.DataFrame, dfrom: date, dto: date) -> pd.DataFrame:
    if "date" not in df.columns:
        return df.copy()

    start_dt = datetime.combine(dfrom, datetime.min.time())
    end_dt = datetime.combine(dto + timedelta(days=1), datetime.min.time())
    return df[(df["date"] >= start_dt) & (df["date"] < end_dt)].copy()

def render_ticket_dashboard(df: pd.DataFrame, dfrom: date, dto: date, accent: str):
    st.subheader("🎫 Ticket Dashboard")

    dfx = _prepare_ticket_df(df)
    cur = _filter_period(dfx, dfrom, dto)

    total = len(cur)
    resolved = int((cur.get("status", pd.Series(dtype=str)) == "Шийдвэрлэсэн").sum())
    accepted = int((cur.get("status", pd.Series(dtype=str)) == "Хүлээн авсан").sum())
    checking = int((cur.get("status", pd.Series(dtype=str)) == "Шалгаж байгаа").sum())
    transferred = int((cur.get("status", pd.Series(dtype=str)) == "Шилжүүлсэн").sum())

    rep_top10 = pd.DataFrame(columns=["item", "count"])
    if "issue_type" in cur.columns:
        rep = cur["issue_type"].dropna().astype(str).str.strip()
        rep = rep[rep != ""]
        rep_counts = rep.value_counts().head(10)
        rep_top10 = rep_counts.reset_index()
        rep_top10.columns = ["item", "count"]

    op_top10 = pd.DataFrame(columns=["operator", "resolved_count"])
    if {"status", "operator_name"}.issubset(cur.columns):
        resolved_df = cur[cur["status"] == "Шийдвэрлэсэн"].copy()
        op_counts = resolved_df["operator_name"].value_counts().head(10)
        op_top10 = op_counts.reset_index()
        op_top10.columns = ["operator", "resolved_count"]

    ch_counts = pd.DataFrame(columns=["channel", "count"])
    if "channel" in cur.columns:
        vc = cur["channel"].dropna().astype(str).str.strip()
        vc = vc[vc != ""]
        vc = vc.value_counts()
        ch_counts = vc.reset_index()
        ch_counts.columns = ["channel", "count"]

    status_trend = pd.DataFrame(columns=["date_only", "status", "count"])
    if {"date", "status"}.issubset(cur.columns):
        t = cur.copy()
        t["date_only"] = t["date"].dt.date
        status_trend = t.groupby(["date_only", "status"]).size().reset_index(name="count")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Шийдвэрлэсэн", f"{resolved:,}")
    c2.metric("Хүлээн авсан", f"{accepted:,}")
    c3.metric("Шалгаж байгаа", f"{checking:,}")
    c4.metric("Шилжүүлсэн", f"{transferred:,}")

    c5, c6 = st.columns(2)
    c5.metric("Нийт тикет", f"{total:,}")
    c6.metric("Resolution rate", f"{(resolved / total * 100):.1f}%" if total else "0.0%")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("#### 📡 Суваг тус бүрийн тикет")
        if ch_counts.empty:
            st.info("Дата алга")
        else:
            ch = alt.Chart(ch_counts).mark_bar(color=accent, cornerRadiusEnd=6).encode(
                y=alt.Y("channel:N", sort="-x", title=""),
                x=alt.X("count:Q", title="Тоо"),
                tooltip=["channel:N", "count:Q"]
            ).properties(height=300)
            st.altair_chart(ch, use_container_width=True)

    with right:
        st.markdown("#### 📊 Статусын өдөр тутмын хуваарилалт")
        if status_trend.empty:
            st.info("Дата алга")
        else:
            color_scale = alt.Scale(
                domain=["Шийдвэрлэсэн", "Хүлээн авсан", "Шалгаж байгаа", "Шилжүүлсэн"],
                range=[accent, "#56B4FF", "#7D8CFF", "#AEB4C5"]
            )
            ch2 = alt.Chart(status_trend).mark_bar().encode(
                x=alt.X("date_only:T", title="Огноо"),
                y=alt.Y("count:Q", title="Тоо"),
                color=alt.Color("status:N", title="Статус", scale=color_scale),
                tooltip=["date_only:T", "status:N", "count:Q"]
            ).properties(height=300)
            st.altair_chart(ch2, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔁 Давтагдсан асуудал (Top 10)")
        if rep_top10.empty:
            st.info("Дата алга")
        else:
            bar1 = alt.Chart(rep_top10).mark_bar(color=accent, cornerRadiusEnd=6).encode(
                y=alt.Y("item:N", sort="-x", title=""),
                x=alt.X("count:Q", title="Тоо"),
                tooltip=["item:N", "count:Q"]
            ).properties(height=320)
            st.altair_chart(bar1, use_container_width=True)

    with col2:
        st.markdown("#### 🏆 Хамгийн олон шийдсэн ажилтан (Top 10)")
        if op_top10.empty:
            st.info("Дата алга")
        else:
            bar2 = alt.Chart(op_top10).mark_bar(color="#56B4FF", cornerRadiusEnd=6).encode(
                y=alt.Y("operator:N", sort="-x", title=""),
                x=alt.X("resolved_count:Q", title="Шийдсэн"),
                tooltip=["operator:N", "resolved_count:Q"]
            ).properties(height=320)
            st.altair_chart(bar2, use_container_width=True)

    st.divider()
    st.markdown("#### 📋 Дэлгэрэнгүй жагсаалт")
    st.dataframe(cur, use_container_width=True, height=360)