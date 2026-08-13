import requests
import streamlit as st
from frontend.config import API_BASE_URL, AUTH_BASE_URL
from frontend.state import decode_jwt_user_id

def get_headers():
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}

def refresh_access():
    if not st.session_state.refresh_token:
        return False
    try:
        r = requests.post(
            f"{AUTH_BASE_URL}/token/refresh/",
            json={"refresh": st.session_state.refresh_token},
            timeout=10,
        )
        if r.status_code == 200:
            st.session_state.access_token = r.json().get("access")
            return True
    except Exception:
        pass
    return False

def api_request(method, url, *, json_body=None, auth=False, retry=True, params=None):
    headers = get_headers() if auth else {}
    try:
        r = requests.request(method, url, json=json_body, headers=headers, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if r.status_code == 401 and auth and retry:
        if refresh_access():
            return api_request(method, url, json_body=json_body, auth=auth, retry=False, params=params)
    return r, None

# --- Auth ---
def do_login(username, password):
    try:
        r = requests.post(f"{AUTH_BASE_URL}/login/", json={"username": username, "password": password}, timeout=10)
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return False
    if r.status_code == 200:
        data = r.json()
        st.session_state.access_token = data.get("access")
        st.session_state.refresh_token = data.get("refresh")
        st.session_state.username = username
        st.session_state.user_id = decode_jwt_user_id(data.get("access"))
        return True
    st.error("Invalid credentials.")
    return False

def do_register(username, password, password2, email):
    payload = {"username": username, "password": password, "password2": password2}
    if email: payload["email"] = email
    try:
        r = requests.post(f"{AUTH_BASE_URL}/register/", json=payload, timeout=10)
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return False
    if r.status_code == 201:
        st.success("✅ Registration successful! You can log in now.")
        return True
    st.error(f"Registration failed: {r.text}")
    return False

def do_logout():
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.editing_post_id = None
    st.session_state.viewing_user_id = None
    st.session_state.current_page = "Home"

# --- Users / Profile ---
def fetch_users(search=""):
    params = {"search": search} if search else {}
    r, err = api_request("GET", f"{API_BASE_URL}/users/", auth=True, params=params)
    if err or r.status_code != 200: return []
    data = r.json()
    return data.get("results", []) if isinstance(data, dict) else data

def fetch_suggested_users():
    r, err = api_request("GET", f"{API_BASE_URL}/users/suggested/", auth=True)
    if err or r.status_code != 200: return []
    data = r.json()
    return data.get("results", []) if isinstance(data, dict) else data

def fetch_user_profile(user_id):
    r, err = api_request("GET", f"{API_BASE_URL}/users/{user_id}/", auth=True)
    if err or r.status_code != 200: return None
    return r.json()

def fetch_my_profile():
    r, err = api_request("GET", f"{API_BASE_URL}/profile/me/", auth=True)
    if err or r.status_code != 200: return None
    return r.json()

def update_my_profile(bio, allow_likes_from, allow_comments_from):
    payload = {"bio": bio, "allow_likes_from": allow_likes_from, "allow_comments_from": allow_comments_from}
    r, err = api_request("PATCH", f"{API_BASE_URL}/profile/me/", auth=True, json_body=payload)
    if err or r.status_code != 200:
        st.error(f"Failed to update profile: {err or r.text}")
        return False
    st.success("Profile updated successfully!")
    return True

# --- Follow ---
def toggle_follow(user_id, is_following):
    method = "DELETE" if is_following else "POST"
    r, err = api_request(method, f"{API_BASE_URL}/users/{user_id}/follow/", auth=True)
    if err or r.status_code not in (200, 204):
        st.error(f"Failed to update follow status: {err or r.text}")
        return False
    return True

def fetch_followers(user_id):
    r, err = api_request("GET", f"{API_BASE_URL}/users/{user_id}/followers/", auth=True)
    if err or r.status_code != 200: return []
    data = r.json()
    return data.get("results", []) if isinstance(data, dict) else data

def fetch_following(user_id):
    r, err = api_request("GET", f"{API_BASE_URL}/users/{user_id}/following/", auth=True)
    if err or r.status_code != 200: return []
    data = r.json()
    return data.get("results", []) if isinstance(data, dict) else data

def fetch_mutual_friends(user_id):
    r, err = api_request("GET", f"{API_BASE_URL}/users/{user_id}/mutual-friends/", auth=True)
    if err or r.status_code != 200: return []
    data = r.json()
    return data.get("results", []) if isinstance(data, dict) else data

# --- Posts ---
def fetch_posts(page=1, search="", endpoint="/posts/"):
    params = {"page": page, "page_size": 10}
    if search: params["search"] = search
    auth = bool(st.session_state.access_token)
    r, err = api_request("GET", f"{API_BASE_URL}{endpoint}", auth=auth, params=params)
    if err or r.status_code != 200: return [], 0, None, None
    data = r.json()
    results = data.get("results", []) if isinstance(data, dict) else data
    count = data.get("count", len(results)) if isinstance(data, dict) else len(results)
    return results, count, data.get("next"), data.get("previous")

def fetch_user_posts(user_id, page=1):
    params = {"page": page, "page_size": 10, "author": user_id}
    auth = bool(st.session_state.access_token)
    r, err = api_request("GET", f"{API_BASE_URL}/posts/", auth=auth, params=params)
    if err or r.status_code != 200: return [], 0, None, None
    data = r.json()
    results = data.get("results", []) if isinstance(data, dict) else data
    count = data.get("count", len(results)) if isinstance(data, dict) else len(results)
    return results, count, data.get("next"), data.get("previous")

def create_post(title, content):
    r, err = api_request("POST", f"{API_BASE_URL}/posts/", json_body={"title": title, "content": content}, auth=True)
    if err:
        st.error(err)
        return False
    if r.status_code == 201:
        st.success("🎉 Post published!")
        return True
    st.error(f"Failed to create post: {r.text}")
    return False

def delete_post(post_id):
    r, err = api_request("DELETE", f"{API_BASE_URL}/posts/{post_id}/", auth=True)
    if err:
        st.error(err)
        return False
    if r.status_code in (200, 204):
        st.success("🗑️ Post deleted.")
        return True
    st.error(f"Failed to delete post: {r.text}")
    return False

def toggle_like(post_id, is_liked):
    method = "DELETE" if is_liked else "POST"
    r, err = api_request(method, f"{API_BASE_URL}/posts/{post_id}/like/", auth=True)
    if err or r.status_code not in (200, 204):
        st.error(f"Failed to update like: {err or r.text}")
        return False
    return True

def toggle_save(post_id, is_saved):
    method = "DELETE" if is_saved else "POST"
    r, err = api_request(method, f"{API_BASE_URL}/posts/{post_id}/save/", auth=True)
    if err or r.status_code not in (200, 204):
        st.error(f"Failed to update save: {err or r.text}")
        return False
    return True

# --- Comments ---
def fetch_comments(post_id):
    auth = bool(st.session_state.access_token)
    r, err = api_request("GET", f"{API_BASE_URL}/posts/{post_id}/comments/?page_size=100", auth=auth)
    if err or r.status_code != 200: return []
    data = r.json()
    return data.get("results", []) if isinstance(data, dict) else data

def create_comment(post_id, text):
    r, err = api_request("POST", f"{API_BASE_URL}/posts/{post_id}/comments/", json_body={"text": text}, auth=True)
    if err:
        st.error(err)
        return False
    if r.status_code == 201:
        st.success("💬 Comment added!")
        return True
    st.error(f"Failed to add comment: {r.text}")
    return False

def delete_comment(comment_id):
    r, err = api_request("DELETE", f"{API_BASE_URL}/comments/{comment_id}/", auth=True)
    if err:
        st.error(err)
        return False
    if r.status_code in (200, 204):
        st.success("🗑️ Comment deleted.")
        return True
    st.error(f"Failed to delete comment: {r.text}")
    return False

# --- Notifications ---
def fetch_notifications():
    r, err = api_request("GET", f"{API_BASE_URL}/notifications/", auth=True)
    if err or r.status_code != 200: return []
    data = r.json()
    return data.get("results", []) if isinstance(data, dict) else data

def mark_notifications_read():
    r, err = api_request("POST", f"{API_BASE_URL}/notifications/read/", auth=True)
    if err or r.status_code != 200: return False
    return True
