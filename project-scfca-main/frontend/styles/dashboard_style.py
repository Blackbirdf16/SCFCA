# Shared style helpers for SCFCA dark dashboard
import streamlit as st

def inject_dashboard_css():
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #181A20 !important;
            color: #F5F6FA !important;
        }
        .css-1d391kg, .css-1v0mbdj, .stSidebar, .st-bb, .st-c6, .st-c7 {
            background-color: #222531 !important;
        }
        .st-cg, .st-cf, .st-cd, .st-ce, .st-cb, .st-cc {
            background-color: #23262F !important;
        }
        .stButton>button, .stTextInput>div>div>input, .stSelectbox>div>div>div>input {
            background-color: #23262F !important;
            color: #F5F6FA !important;
        }
        .stButton>button {
            border: 1px solid #F0B90B !important;
            color: #F0B90B !important;
            font-weight: 600;
        }
        .st-bb, .st-c6, .st-c7 {
            border-radius: 12px !important;
        }
        .kpi-card {
            background: #23262F;
            border-radius: 12px;
            padding: 1.5rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px #0002;
            color: #F5F6FA;
            text-align: center;
        }
        .kpi-title {
            font-size: 1rem;
            color: #F0B90B;
            margin-bottom: 0.25rem;
        }
        .kpi-value {
            font-size: 2.2rem;
            font-weight: 700;
        }
        .status-badge {
            display: inline-block;
            padding: 0.2em 0.8em;
            border-radius: 8px;
            font-size: 0.9em;
            font-weight: 600;
            margin-right: 0.5em;
        }
        .status-pending { background: #F0B90B22; color: #F0B90B; }
        .status-approved { background: #1FC77A22; color: #1FC77A; }
        .status-rejected { background: #F6465D22; color: #F6465D; }
        .sidebar-title {
            color: #F0B90B !important;
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            margin-bottom: 1.5rem !important;
        }
        .role-badge {
            background: #23262F;
            color: #F0B90B;
            border: 1px solid #F0B90B;
            border-radius: 8px;
            padding: 0.2em 0.8em;
            font-size: 0.9em;
            font-weight: 600;
            margin-left: 0.5em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def kpi_card(title, value):
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-title'>{title}</div>
            <div class='kpi-value'>{value}</div>
        </div>
    """, unsafe_allow_html=True)
