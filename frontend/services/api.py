import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

def login(username, password):
    try:
        resp = requests.post(f"{API_URL}/api/v1/auth/login", json={"username": username, "password": password})
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("detail", "Login failed.")
    except Exception as e:
        return None, str(e)

def get_dashboard(token):
    try:
        resp = requests.get(f"{API_URL}/api/v1/dashboard/summary", cookies={"session": token})
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("detail", "No dashboard data.")
    except Exception as e:
        return None, str(e)

def get_cases(token):
    try:
        resp = requests.get(f"{API_URL}/api/v1/cases/", cookies={"session": token})
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("detail", "No cases found.")
    except Exception as e:
        return None, str(e)

def get_assets(token):
    try:
        resp = requests.get(f"{API_URL}/api/v1/assets/", cookies={"session": token})
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("detail", "No assets found.")
    except Exception as e:
        return None, str(e)

def get_tickets(token):
    try:
        resp = requests.get(f"{API_URL}/api/v1/tickets/", cookies={"session": token})
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("detail", "No tickets found.")
    except Exception as e:
        return None, str(e)

def get_audit(token):
    try:
        resp = requests.get(f"{API_URL}/api/v1/audit/", cookies={"session": token})
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("detail", "No audit events found.")
    except Exception as e:
        return None, str(e)

def get_documents(token):
    try:
        resp = requests.get(f"{API_URL}/api/v1/documents/", cookies={"session": token})
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("detail", "No documents found.")
    except Exception as e:
        return None, str(e)
