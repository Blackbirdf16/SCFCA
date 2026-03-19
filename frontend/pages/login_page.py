import streamlit as st
from frontend.services import api

def login_page():
    st.title("SCFCA Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user, error = api.login(username, password)
        if user:
            st.session_state.token = user.get("token", "demo-token")
            st.session_state.user = user.get("username", username)
            st.success("Login successful!")
        else:
            st.error(error or "Login failed.")
    if st.session_state.get("token"):
        st.info(f"Logged in as: {st.session_state.user}")
