import streamlit as st
import pandas as pd
import json
import os
import time
import plotly.io as pio
from typing import Dict, Any

from database import init_db, register_user, authenticate_user, save_analysis_history, get_user_history
from crew import AutoInsightCrew
from tools import profile_csv_dataset, generate_plotly_chart_config

# Page Configuration
st.set_page_config(
    page_title="AutoInsight AI - Autonomous Data Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38BDF8;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-tracker {
        background-color: #1E293B;
        border-left: 4px solid #2563EB;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E293B;
        border-radius: 6px 6px 0 0;
        padding: 10px 20px;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

# Initialize Database Schema
init_db()

# User Authentication Logic in Sidebar
st.sidebar.title("🤖 AutoInsight AI")

if not st.session_state.authenticated:
    st.sidebar.subheader("Authentication")
    auth_mode = st.sidebar.radio("Choose Action", ["Login", "Sign Up"])
    
    email_input = st.sidebar.text_input("Email Address")
    password_input = st.sidebar.text_input("Password", type="password")
    
    if auth_mode == "Sign Up":
        if st.sidebar.button("Register Account", use_container_width=True):
            if email_input and password_input:
                if register_user(email_input, password_input):
                    st.sidebar.success("Account created! Please log in.")
                else:
                    st.sidebar.error("Email already registered.")
            else:
                st.sidebar.warning("Please fill out all fields.")
                
    elif auth_mode == "Login":
        if st.sidebar.button("Sign In", use_container_width=True):
            if authenticate_user(email_input, password_input):
                st.session_state.authenticated = True
                st.session_state.user_email = email_input.strip().lower()
                st.rerun()
            else:
                st.sidebar.error("Invalid email or password.")
                
    st.markdown('<div class="main-header">Welcome to AutoInsight AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Autonomous Multi-Agent Data Analytics Platform</div>', unsafe_allow_html=True)
    
    st.info("👈 Please **Sign In** or **Register** using the sidebar to begin analyzing your datasets.")
    
    st.markdown("### Platform Features")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">01</div>
            <div class="metric-label">Deterministic Profiling</div>
            <p style="font-size:0.85rem; color:#94A3B8; margin-top:0.5rem;">Pure Python computation for zero mathematical hallucination.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_f2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">02</div>
            <div class="metric-label">Multi-Agent AI</div>
            <p style="font-size:0.85rem; color:#94A3B8; margin-top:0.5rem;">Orchestrated CrewAI squad driven by Groq LLM inference.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_f3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">03</div>
            <div class="metric-label">Executive Reports</div>
            <p style="font-size:0.85rem; color:#94A3B8; margin-top:0.5rem;">Downloadable publication-ready PDF summaries and Plotly charts.</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Logged-in Header & Navigation
    st.sidebar.markdown(f"**Logged in as:** `{st.session_state.user_email}`")
    if st.sidebar.button("Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.session_state.current_analysis = None
        st.rerun()
        
    st.markdown('<div class="main-header">AutoInsight AI Analytics Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Transform raw datasets into actionable executive intelligence in seconds.</div>', unsafe_allow_html=True)

    tab_analytics, tab_history = st.tabs(["🚀 New Analysis", "📜 My Saved Analyses"])

    # TAB 1: CSV Upload & Multi-Agent Execution
    with tab_analytics:
        st.subheader("1. Upload CSV Dataset")
        uploaded_file = st.file_uploader("Choose a CSV file (Max 100MB)", type=["csv"])

        if uploaded_file is not None:
            # Save uploaded CSV locally to temp path
            os.makedirs("data_temp", exist_ok=True)
            temp_path = os.path.join("data_temp", uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Dataset Quick Preview
            df_preview = pd.read_csv(temp_path)
            st.markdown(f"**Loaded File:** `{uploaded_file.name}` | **Rows:** {df_preview.shape[0]:,} | **Columns:** {df_preview.shape[1]}")
            
            with st.expander("🔍 Preview Raw Dataset (First 5 Rows)", expanded=False):
                st.dataframe(df_preview.head(5), use_container_width=True)

            st.subheader("2. Analytical Focus & Execution")
            user_query = st.text_input(
                "Optional Custom Intent / Business Question",
                placeholder="e.g., Identify top customer churn drivers and outline key growth recommendations."
            )

            if st.button("▶ Run Multi-Agent Analysis Pipeline", type="primary", use_container_width=True):
                # Check for GROQ API Key
                if not os.environ.get("GROQ_API_KEY") and "GROQ_API_KEY" in st.secrets:
                    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

                if not os.environ.get("GROQ_API_KEY"):
                    st.error("⚠️ GROQ_API_KEY is missing! Set it in your environment or Streamlit Secrets.")
                else:
                    status_box = st.empty()
                    
                    # Agent Execution Simulation & Tracking
                    with status_box.container():
                        st.markdown("""
                        <div class="status-tracker">
                            <b>🔄 Multi-Agent Pipeline Active...</b><br/>
                            🔹 <i>Manager Agent</i>: Initializing schema parsing and intent strategy...
                        </div>
                        """, unsafe_allow_html=True)
                    time.sleep(1)

                    with status_box.container():
                        st.markdown("""
                        <div class="status-tracker">
                            <b>🔄 Multi-Agent Pipeline Active...</b><br/>
                            🔹 <i>Data Analyst Agent</i>: Computing missingness, descriptive stats, and Plotly configs...
                        </div>
                        """, unsafe_allow_html=True)

                    # Instantiate and run Crew
                    crew_runner = AutoInsightCrew(file_path=temp_path, user_query=user_query)
                    results = crew_runner.run()

                    with status_box.container():
                        st.markdown("""
                        <div class="status-tracker">
                            <b>🔄 Multi-Agent Pipeline Active...</b><br/>
                            🔹 <i>Insights & Reporting Agent</i>: Synthesizing executive summaries and creating PDF brief...
                        </div>
                        """, unsafe_allow_html=True)
                    time.sleep(1)

                    status_box.success("✅ Multi-Agent Analysis Complete!")

                    # Persist results in SQLite
                    history_id = save_analysis_history(
                        user_email=st.session_state.user_email,
                        file_name=uploaded_file.name,
                        data_summary=results["data_summary"],
                        executive_report=results["executive_report"]
                    )

                    st.session_state.current_analysis = results
                    st.rerun()

        # Render Active Analysis Output Dashboard
        if st.session_state.current_analysis:
            st.markdown("---")
            st.subheader("3. Executive Dashboard & Findings")

            analysis_data = st.session_state.current_analysis
            summary = analysis_data.get("data_summary", {})
            report_text = analysis_data.get("executive_report", "")

            # Overview Metrics
            if "overview" in summary:
                ov = summary["overview"]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Rows", f"{ov.get('total_rows', 0):,}")
                c2.metric("Total Columns", ov.get('total_columns', 0))
                c3.metric("Duplicate Rows", ov.get('duplicate_rows', 0))
                c4.metric("Numeric Columns", ov.get('numeric_columns_count', 0))

            st.markdown("### Executive Summary Brief")
            st.markdown(report_text)

            # Interactive Plotly Chart Display
            st.markdown("### Data Visualizations")
            if "numeric_summary" in summary and summary["numeric_summary"]:
                numeric_cols = list(summary["numeric_summary"].keys())
                if len(numeric_cols) >= 1:
                    col_x = numeric_cols[0]
                    col_y = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
                    
                    chart_json_str = generate_plotly_chart_config.run(
                        file_path=temp_path,
                        chart_type="scatter" if len(numeric_cols) > 1 else "histogram",
                        x_axis=col_x,
                        y_axis=col_y if len(numeric_cols) > 1 else "",
                        title=f"{col_x} vs {col_y}" if len(numeric_cols) > 1 else f"Distribution of {col_x}"
                    )
                    
                    try:
                        chart_data = json.loads(chart_json_str)
                        if "plotly_json" in chart_data:
                            fig = pio.from_json(json.dumps(chart_data["plotly_json"]))
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.info("Generating standard distribution chart...")

            # PDF Download Handler
            st.markdown("### Download Deliverables")
            pdf_file_path = analysis_data.get("pdf_path", "reports/AutoInsight_Executive_Report.pdf")
            if os.path.exists(pdf_file_path):
                with open(pdf_file_path, "rb") as pdf_file:
                    st.download_button(
                        label="📄 Download Executive PDF Report",
                        data=pdf_file,
                        file_name=f"AutoInsight_Report_{int(time.time())}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

    # TAB 2: User Analysis History
    with tab_history:
        st.subheader("My Saved Historical Analyses")
        user_records = get_user_history(st.session_state.user_email)

        if not user_records:
            st.info("No saved historical analyses found. Run a new analysis in Tab 1!")
        else:
            for record in user_records:
                with st.expander(f"📁 {record['file_name']} — Analyzed on {record['created_at']}", expanded=False):
                    st.markdown("**Overview Summary:**")
                    ov = record["data_summary"].get("overview", {})
                    st.write(f"- Rows: {ov.get('total_rows', 'N/A')} | Columns: {ov.get('total_columns', 'N/A')}")
                    
                    st.markdown("**Executive Report:**")
                    st.markdown(record["executive_report"])
