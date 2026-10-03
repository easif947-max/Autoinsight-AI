import sys
import os

# Fix import paths for Streamlit Cloud execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import json
import time
import plotly.io as pio

from database import init_db, register_user, authenticate_user, save_analysis_history, get_user_history
from crew import AutoInsightCrew
from tools.chart_generator_tool import generate_plotly_chart_config

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

else:
    # Logged-in Navigation
    st.sidebar.markdown(f"**Logged in as:** `{st.session_state.user_email}`")
    if st.sidebar.button("Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.session_state.current_analysis = None
        st.rerun()
        
    st.markdown('<div class="main-header">AutoInsight AI Analytics Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Transform raw datasets into actionable executive intelligence.</div>', unsafe_allow_html=True)

    tab_analytics, tab_history = st.tabs(["🚀 New Analysis", "📜 My Saved Analyses"])

    # TAB 1: CSV Upload & Pipeline Engine
    with tab_analytics:
        st.subheader("1. Upload CSV Dataset")
        uploaded_file = st.file_uploader("Choose a CSV file (Max 100MB)", type=["csv"])

        if uploaded_file is not None:
            os.makedirs("data_temp", exist_ok=True)
            temp_path = os.path.join("data_temp", uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            df_preview = pd.read_csv(temp_path)
            st.markdown(f"**Loaded File:** `{uploaded_file.name}` | **Rows:** {df_preview.shape[0]:,} | **Columns:** {df_preview.shape[1]}")
            
            with st.expander("🔍 Preview Raw Dataset", expanded=False):
                st.dataframe(df_preview.head(5), use_container_width=True)

            st.subheader("2. Analytical Focus & Execution")
            user_query = st.text_input(
                "Optional Business Question",
                placeholder="e.g., Identify main revenue drivers and outlier trends."
            )

            if st.button("▶ Run Multi-Agent Analysis Pipeline", type="primary", use_container_width=True):
                # Check for GROQ_API_KEY in Streamlit Secrets
                if not os.environ.get("GROQ_API_KEY") and "GROQ_API_KEY" in st.secrets:
                    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

                if not os.environ.get("GROQ_API_KEY"):
                    st.error("⚠️ GROQ_API_KEY is missing! Please set it in Streamlit Secrets.")
                else:
                    status_box = st.empty()
                    
                    with status_box.container():
                        st.markdown("""
                        <div class="status-tracker">
                            <b>🔄 Multi-Agent Pipeline Running...</b><br/>
                            🔹 <i>Manager Agent</i>: Orchestrating workflow...
                        </div>
                        """, unsafe_allow_html=True)
                    time.sleep(1)

                    with status_box.container():
                        st.markdown("""
                        <div class="status-tracker">
                            <b>🔄 Multi-Agent Pipeline Running...</b><br/>
                            🔹 <i>Data Analyst Agent</i>: Calculating statistical metrics...
                        </div>
                        """, unsafe_allow_html=True)

                    # Execute Crew Workflow
                    crew_runner = AutoInsightCrew(file_path=temp_path, user_query=user_query)
                    results = crew_runner.run()

                    with status_box.container():
                        st.markdown("""
                        <div class="status-tracker">
                            <b>🔄 Multi-Agent Pipeline Running...</b><br/>
                            🔹 <i>Insights Agent</i>: Generating final executive brief...
                        </div>
                        """, unsafe_allow_html=True)
                    time.sleep(1)

                    status_box.success("✅ Multi-Agent Analysis Complete!")

                    # Save result to SQLite
                    save_analysis_history(
                        user_email=st.session_state.user_email,
                        file_name=uploaded_file.name,
                        data_summary=results["data_summary"],
                        executive_report=results["executive_report"]
                    )

                    st.session_state.current_analysis = results
                    st.rerun()

        # Render Active Analysis Results
        if st.session_state.current_analysis:
            st.markdown("---")
            st.subheader("3. Executive Dashboard & Findings")

            analysis_data = st.session_state.current_analysis
            summary = analysis_data.get("data_summary", {})
            report_text = analysis_data.get("executive_report", "")

            if "overview" in summary:
                ov = summary["overview"]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Rows", f"{ov.get('total_rows', 0):,}")
                c2.metric("Total Columns", ov.get('total_columns', 0))
                c3.metric("Duplicate Rows", ov.get('duplicate_rows', 0))
                c4.metric("Numeric Columns", ov.get('numeric_columns_count', 0))

            st.markdown("### Executive Summary Brief")
            st.markdown(report_text)

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
