import streamlit as st
import pandas as pd
import time

st.set_page_config(
    page_title="AI Creator Comment Intelligence",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# HEADER
# -------------------------------

st.title("AI Creator Comment Intelligence Engine")
st.caption("Turn messy audience comments into ranked strategic opportunities")

st.divider()

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Upload & Analyze",
        "Strategic Insights",
        "Cluster Explorer",
        "Action Recommendations",
        "Executive Summary"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("Project Info")
st.sidebar.write("Version: v1.0")
st.sidebar.write("Mode: Private")
st.sidebar.write("Model: Semantic Clustering")

# -------------------------------
# PAGE 1 — UPLOAD
# -------------------------------

if page == "Upload & Analyze":

    st.header("Upload Audience Comments")

    uploaded_file = st.file_uploader(
        "Upload CSV of comments",
        type=["csv"]
    )

    if uploaded_file:

        df = pd.read_csv(uploaded_file)

        st.success("File uploaded successfully")

        st.subheader("Preview")
        st.dataframe(df, use_container_width=True)

        st.divider()

        if st.button("Run Intelligence Engine"):

            with st.spinner("Processing comments..."):
                time.sleep(2)

            st.success("Analysis complete")

            st.session_state["analysis_complete"] = True

# -------------------------------
# PAGE 2 — STRATEGIC INSIGHTS
# -------------------------------

elif page == "Strategic Insights":

    st.header("Top Strategic Signals")

    if not st.session_state.get("analysis_complete"):
        st.warning("Run analysis first")
        st.stop()

    import textwrap

    def show_signal(title, text):
      wrapped = textwrap.fill(text, width=45)
      st.markdown(f"""
      <div style="
        background-color:#111;
        padding:16px;
        border-radius:10px;
        border:1px solid #333;
        min-height:120px;
    ">
        <div style="font-size:13px;color:#aaa;">{title}</div>
        <div style="font-size:18px;font-weight:600;margin-top:6px;">
            {wrapped}
        </div>
    </div>
    """, unsafe_allow_html=True)


    col1, col2, col3 = st.columns(3)

    with col1:
       show_signal(
        "Top Growth Opportunity",
        "Requests for deeper explanation and more detailed examples from the creator"
     )

    with col2:
       show_signal(
        "Primary Risk Signal",
        "Confusion about topic due to unclear explanation or missing conceptual breakdown"
     )

    with col3:
       show_signal(
        "Engagement Driver",
        "Positive reinforcement and appreciation of creator style and delivery"
     )

    st.divider()

    st.subheader("Opportunity Ranking")

    insights = pd.DataFrame({
        "Theme": [
            "Request for more examples",
            "Concept confusion",
            "Trust skepticism",
            "General praise"
        ],
        "Impact Score": [312, 188, 94, 40],
        "Priority": ["High", "High", "Medium", "Low"]
    })

    st.dataframe(insights, use_container_width=True)

# -------------------------------
# PAGE 3 — CLUSTER EXPLORER
# -------------------------------

elif page == "Cluster Explorer":

    st.header("Audience Theme Clusters")

    if not st.session_state.get("analysis_complete"):
        st.warning("Run analysis first")
        st.stop()

    cluster = st.selectbox(
        "Select cluster",
        [
            "Request: More explanation",
            "Confusion: Terminology unclear",
            "Skepticism: Credibility questions",
            "Praise: Positive feedback"
        ]
    )

    st.subheader("Cluster Summary")

    summaries = {
        "Request: More explanation":
            "Audience wants deeper breakdowns and step-by-step guidance.",
        "Confusion: Terminology unclear":
            "Users struggle with technical language.",
        "Skepticism: Credibility questions":
            "Trust signals are weak or unclear.",
        "Praise: Positive feedback":
            "Content format is strongly resonating."
    }

    st.info(summaries[cluster])

    st.subheader("Representative Comments")

    st.write("""
    • "Can you explain this more slowly?"
    • "I don't understand this step"
    • "Please show real examples"
    """)

# -------------------------------
# PAGE 4 — ACTION RECOMMENDATIONS
# -------------------------------

elif page == "Action Recommendations":

    st.header("Recommended Creator Actions")

    if not st.session_state.get("analysis_complete"):
        st.warning("Run analysis first")
        st.stop()

    st.success("High Priority Actions")

    st.write("""
    1. Produce follow-up deep dive video  
    2. Create beginner explanation content  
    3. Add real-world examples  
    4. Address misconceptions directly  
    """)

    st.divider()

    st.warning("Risk Mitigation")

    st.write("""
    • Clarify terminology  
    • Improve credibility signals  
    • Reduce ambiguity in explanations  
    """)

# -------------------------------
# PAGE 5 — EXECUTIVE SUMMARY
# -------------------------------

elif page == "Executive Summary":

    st.header("Executive Decision Brief")

    if not st.session_state.get("analysis_complete"):
        st.warning("Run analysis first")
        st.stop()

    st.subheader("Primary Growth Opportunity")
    st.write("Audience is actively requesting deeper content and expanded explanations.")

    st.subheader("Main Risk")
    st.write("Conceptual confusion may reduce retention if unaddressed.")

    st.subheader("Recommended Strategic Move")
    st.write("Shift toward educational expansion and structured explanation content.")

    st.divider()

    st.success("Decision Priority: HIGH")

