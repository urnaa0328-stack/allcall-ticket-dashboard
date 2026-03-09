import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date

def _prepare_social_df(df: pd.DataFrame) -> pd.DataFrame:
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

def render_social_dashboard(df: pd.DataFrame, dfrom: date, dto: date, accent: str):
    st.subheader("📣 Social Media Dashboard")

    dfx = _prepare_social_df(df)
    cur = _filter_period(dfx, dfrom, dto)

    total_views = float(pd.to_numeric(cur.get("post_views", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "post_views" in cur.columns else 0.0
    total_viewers = float(pd.to_numeric(cur.get("viewers", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "viewers" in cur.columns else 0.0
    total_conv = float(pd.to_numeric(cur.get("conversations_started", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "conversations_started" in cur.columns else 0.0
    total_spend_usd = float(pd.to_numeric(cur.get("total_spend_usd", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "total_spend_usd" in cur.columns else 0.0
    total_spend_mnt = float(pd.to_numeric(cur.get("total_spend_mnt", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "total_spend_mnt" in cur.columns else 0.0
    cpc = (total_spend_usd / total_conv) if total_conv else 0.0

    platform_df = pd.DataFrame(columns=["platform", "spend"])
    if "platform" in cur.columns and "total_spend_mnt" in cur.columns:
        tmp = cur.copy()
        tmp["total_spend_mnt"] = pd.to_numeric(tmp["total_spend_mnt"], errors="coerce").fillna(0)
        platform_df = tmp.groupby("platform", as_index=False)["total_spend_mnt"].sum()
        platform_df.columns = ["platform", "spend"]

    campaign_df = pd.DataFrame(columns=["campaign_name", "conversations_started"])
    if "campaign_name" in cur.columns and "conversations_started" in cur.columns:
        tmp = cur.copy()
        tmp["conversations_started"] = pd.to_numeric(tmp["conversations_started"], errors="coerce").fillna(0)
        campaign_df = tmp.groupby("campaign_name", as_index=False)["conversations_started"].sum()
        campaign_df = campaign_df.sort_values("conversations_started", ascending=False).head(10)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Post views", f"{total_views:,.0f}")
    c2.metric("Viewers", f"{total_viewers:,.0f}")
    c3.metric("Conversations", f"{total_conv:,.0f}")
    c4.metric("Cost / conversation", f"${cpc:,.2f}")

    c5, c6 = st.columns(2)
    c5.metric("Total spend USD", f"${total_spend_usd:,.2f}")
    c6.metric("Total spend MNT", f"₮{total_spend_mnt:,.0f}")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.markdown("#### 💰 Spend by platform")
        if platform_df.empty:
            st.info("Дата алга")
        else:
            ch = alt.Chart(platform_df).mark_bar(color=accent, cornerRadiusEnd=6).encode(
                y=alt.Y("platform:N", sort="-x", title=""),
                x=alt.X("spend:Q", title="Spend (₮)"),
                tooltip=["platform:N", "spend:Q"]
            ).properties(height=300)
            st.altair_chart(ch, use_container_width=True)

    with right:
        st.markdown("#### 📈 Top campaigns by conversations")
        if campaign_df.empty:
            st.info("Дата алга")
        else:
            ch = alt.Chart(campaign_df).mark_bar(color="#56B4FF", cornerRadiusEnd=6).encode(
                y=alt.Y("campaign_name:N", sort="-x", title=""),
                x=alt.X("conversations_started:Q", title="Conversations"),
                tooltip=["campaign_name:N", "conversations_started:Q"]
            ).properties(height=300)
            st.altair_chart(ch, use_container_width=True)

    st.divider()
    st.markdown("#### 📋 Дэлгэрэнгүй жагсаалт")
    st.dataframe(cur, use_container_width=True, height=360)