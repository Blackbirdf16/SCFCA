import streamlit as st
from frontend.services import api
from frontend.pages import (
    login_page, dashboard_page, cases_page, assets_page, tickets_page, audit_page, documents_page
)

PAGES = {
    "Login": login_page,
    "Dashboard": dashboard_page,
    "Cases": cases_page,
    "Assets": assets_page,
    "Tickets": tickets_page,
    "Audit": audit_page,
    "Documents": documents_page,
}

def main():
    st.set_page_config(page_title="SCFCA PoC", layout="wide")
    if "token" not in st.session_state:
        st.session_state.token = None
        st.session_state.user = None
    st.sidebar.title("SCFCA Navigation")
    page = st.sidebar.radio("Go to", list(PAGES.keys()))
    PAGES[page]()

if __name__ == "__main__":
    main()
