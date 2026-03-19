import streamlit as st
from frontend.styles.dashboard_style import inject_dashboard_css
from frontend.pages.login_page import login_page
from frontend.pages.dashboard import dashboard_page
from frontend.pages.cases import cases_page
from frontend.pages.assets import assets_page
from frontend.pages.tickets import tickets_page
from frontend.pages.audit import audit_page
from frontend.pages.documents import documents_page

PAGES = {
    "Dashboard": dashboard_page,
    "Cases": cases_page,
    "Assets": assets_page,
    "Tickets": tickets_page,
    "Audit": audit_page,
    "Documents": documents_page,
}

def main():
    st.set_page_config(page_title="SCFCA PoC", layout="wide")
    inject_dashboard_css()
    if "token" not in st.session_state:
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.role = None

    # Sidebar
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>SCFCA</div>", unsafe_allow_html=True)
        if st.session_state.token:
            nav = st.radio("Navigation", list(PAGES.keys()))
            st.markdown(f"<div style='margin-top:2rem;'><b>User:</b> {st.session_state.user or ''}</div>", unsafe_allow_html=True)
            if st.session_state.role:
                st.markdown(f"<span class='role-badge'>{st.session_state.role}</span>", unsafe_allow_html=True)
            if st.button("Logout"):
                st.session_state.token = None
                st.session_state.user = None
                st.session_state.role = None
                st.experimental_rerun()
        else:
            nav = "Login"

    # Main content
    st.markdown("""
        <div style='min-height: 100vh; background: #181A20; padding: 0; margin: 0;'></div>
    """, unsafe_allow_html=True)
    if nav == "Login":
        login_page()
    else:
        PAGES[nav]()

if __name__ == "__main__":
    main()
