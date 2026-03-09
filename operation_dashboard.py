import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date

def _prepare_operation_df(df: pd.DataFrame) -> pd.DataFrame:
    dfx = df.copy()
    for col in ["start_date", "end_date"]:
        if col in dfx.columns:
            dfx[col] = pd.to_datetime(dfx[col], errors="coerce")
    return dfx

def _filter_period(df: pd.DataFrame, dfrom: date, dto: date) -> pd.DataFrame:
    if "start_date" not in df.columns:
        return df.copy()
    start_dt = datetime.combine(dfrom, datetime.min.time())
    end_dt = datetime.combine(dto + timedelta(days=1), datetime.min.time())
    return df[(df["start_date"] >= start_dt) & (df["start_date"] < end_dt)].copy()

def render_operation_dashboard(df: pd.DataFrame, dfrom: date, dto: date, accent: str):
    st.subheader("🛠 Operation Dashboard")

    dfx = _prepare_operation_df(df)
    cur = _filter_period(dfx, dfrom, dto)

    total_tasks = len(cur)
    completed = int(pd.to_numeric(cur.get("completion_flag", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "completion_flag" in cur.columns else 0
    in_progress = int((cur.get("status", pd.Series(dtype=str)).astype(str) == "Хийгдэж байна").sum())
    waiting = int((cur.get("status", pd.Series(dtype=str)).astype(str) == "Хүлээгдэж байна").sum())
    completion_rate = (completed / total_tasks * 100) if total_tasks else 0.0

    owner_df = pd.DataFrame(columns=["owner", "count"])
    if "owner" in cur.columns:
        vc = cur["owner"].dropna().astype(str).str.strip().value_counts().head(10)
        owner_df = vc.reset_index()
        owner_df.columns = ["owner", "count"]

    dept_df = pd.DataFrame(columns=["department", "count"])
    if "department" in cur.columns:
        vc = cur["department"].dropna().astype(str).str.strip().value_counts()
        dept_df = vc.reset_index()
        dept_df.columns = ["department", "count"]

    status_df = pd.DataFrame(columns=["status", "count"])
    if "status" in cur.columns:
        vc = cur["status"].dropna().astype(str).str.strip().value_counts()
        status_df = vc.reset_index()
        status_df.columns = ["status", "count"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Нийт ажил", f"{total_tasks:,}")
    c2.metric("Хийгдсэн", f"{completed:,}")
    c3.metric("Хийгдэж байна", f"{in_progress:,}")
    c4.metric("Completion rate", f"{completion_rate:.1f}%")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.markdown("#### 👥 Owner workload")
        if owner_df.empty:
            st.info("Дата алга")
        else:
            ch = alt.Chart(owner_df).mark_bar(color=accent, cornerRadiusEnd=6).encode(
                y=alt.Y("owner:N", sort="-x", title=""),
                x=alt.X("count:Q", title="Tasks"),
                tooltip=["owner:N", "count:Q"]
            ).properties(height=300)
            st.altair_chart(ch, use_container_width=True)

    with right:
        st.markdown("#### 🏢 Department distribution")
        if dept_df.empty:
            st.info("Дата алга")
        else:
            ch = alt.Chart(dept_df).mark_arc(innerRadius=60).encode(
                theta="count:Q",
                color=alt.Color("department:N", title="Department"),
                tooltip=["department:N", "count:Q"]
            ).properties(height=300)
            st.altair_chart(ch, use_container_width=True)

    st.divider()
    st.markdown("#### 📌 Status distribution")
    if status_df.empty:
        st.info("Дата алга")
    else:
        bar = alt.Chart(status_df).mark_bar(color="#56B4FF", cornerRadiusEnd=6).encode(
            y=alt.Y("status:N", sort="-x", title=""),
            x=alt.X("count:Q", title="Count"),
            tooltip=["status:N", "count:Q"]
        ).properties(height=320)
        st.altair_chart(bar, use_container_width=True)

    st.divider()
    st.markdown("#### 📋 Дэлгэрэнгүй жагсаалт")
    st.dataframe(cur, use_container_width=True, height=360)