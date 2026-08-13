import streamlit as st
import base64
import json

def init_state():
    defaults = {
        "access_token": None,
        "refresh_token": None,
        "username": None,
        "user_id": None,
        "current_page": "Home",
        "search_query": "",
        "editing_post_id": None,
        "viewing_user_id": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def decode_jwt_user_id(token):
    """Return user_id from a SimpleJWT access token (client-side only)."""
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("user_id")
    except Exception:
        return None
