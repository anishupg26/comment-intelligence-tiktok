import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from intelligence.pipeline import run_intelligence_engine

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AI Creator Comment Intelligence Engine",
    layout="wide"
)

st.title("AI Creator Comment Intelligence Engine")
st.caption("Turn messy comments into ranked, actionable creator insights.")


# --------------------------------------------------
# HTML CLUSTER CARD RENDERER
# --------------------------------------------------
def render_cluster_card(row):

    risk_color = {
        "Retention Risk": "#ff4d4f",
        "Trust Risk": "#faad14",
        "None": "#52c41a"
    }.get(row["risk_flag"], "#999999")

    html = f"""
    <div style="
        padding:18px;
        border-radius:12px;
        border:1px solid #e6e6e6;
        margin-bottom:16px;
        background:white;
        box-shadow:0 1px 2px rgba(0,0,0,0.05);
    ">
        <h3 style="margin:0 0 6px 0;">
            {row['theme']}
        </h3>

        <p style="margin:4px 0 10px 0; color:#666;">
            Classification: <b>{row['classification']}</b> |
            Impact Score: <b>{round(row['impact_score'],2)}</b> |
            Comment Share: <b>{round(row['comment_share_pct'],1)}%</b>
        </p>

        <div style="margin-top:8px;">
            {row['insight']}
        </div>

        <div style="margin-top:10px;">
            <b>Recommended Action:</b><br>
            {row['suggested_action']}
        </div>

        <div style="margin-top:12px;">
            <span style="
                padding:4px 10px;
                border-radius:6px;
                background:{risk_color};
                color:white;
                font-weight:600;
                font-size:12px;
            ">
                {row['risk_flag']}
            </span>
        </div>
    </div>
    """

    components.html(html, height=240)


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader("Upload Comment CSV", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.subheader("Raw Comments")
    st.caption(f"Total comments uploaded: {len(df)}")

    show_all = st.checkbox("Show full dataset")

    if show_all:
      st.dataframe(df, use_container_width=True)
    else:
      st.dataframe(df.head(50), use_container_width=True)

    if st.button("Analyze Comments"):

        with st.spinner("Running intelligence engine..."):
            ranked_df, labeled_df = run_intelligence_engine(df)

        st.success("Analysis complete")

        # --------------------------------------------------
        # METRICS
        # --------------------------------------------------
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Comments", len(labeled_df))
        col2.metric("Audience Signals", len(ranked_df))
        col3.metric("Highest Impact Score", round(ranked_df["impact_score"].max(), 1))

        # --------------------------------------------------
        # EXECUTIVE SUMMARY
        # --------------------------------------------------
        st.subheader("Executive Summary")

        top = ranked_df.iloc[0]

        st.info(
            f"""
Top opportunity: **{top['theme']}**

{round(top['comment_share_pct'],1)}% of comments indicate this demand.

Recommended action:
{top['suggested_action']}
"""
        )

        # --------------------------------------------------
        # PRIORITIZED SIGNALS
        # --------------------------------------------------
        st.subheader("Top Audience Signals")

        for _, row in ranked_df.iterrows():
            render_cluster_card(row)

        # --------------------------------------------------
        # CLUSTER DRILLDOWN
        # --------------------------------------------------
        st.subheader("Cluster Drilldown")

        cluster_ids = ranked_df["cluster_id"].tolist()
        selected = st.selectbox("Select cluster", cluster_ids)

        row = ranked_df[ranked_df["cluster_id"] == selected].iloc[0]

        st.markdown("### Signal Details")
        st.write("Theme:", row["theme"])
        st.write("Classification:", row["classification"])
        st.write("Impact Score:", round(row["impact_score"], 2))

        if row["risk_flag"] == "Retention Risk":
            st.error("Retention Risk")
        elif row["risk_flag"] == "Trust Risk":
            st.warning("Trust Risk")
        else:
            st.success("No Risk")

        st.write("Recommended Action:", row["suggested_action"])

        # --------------------------------------------------
        # EXAMPLE COMMENTS
        # --------------------------------------------------
        st.subheader("Example Comments")

        comments = labeled_df[labeled_df["cluster"] == selected]["comment"].head(10)

        for c in comments:
            st.write("•", c)

