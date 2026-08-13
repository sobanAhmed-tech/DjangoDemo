import streamlit as st
import requests
import datetime
import base64
import json

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api"
AUTH_BASE_URL = "http://127.0.0.1:8000/api/auth"

st.set_page_config(
    page_title="Django Blog",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Custom CSS — attractive header, cards, comments, badges, buttons
# ------------------------------------------------------------------
st.markdown("""
<style>
    /* Page background — follow the active theme (dark) */
    .stApp {
        background-color: var(--background-color);
    }

    /* ---- Hero header ---- */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 38px 40px;
        border-radius: 0 0 24px 24px;
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.35);
        margin: -1.2rem -1.2rem 1.5rem -1.2rem;
        color: white;
    }
    .hero-header h1 {
        margin: 0;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-header p {
        margin: 6px 0 0 0;
        font-size: 1.05rem;
        opacity: 0.92;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.18);
        backdrop-filter: blur(4px);
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 0.8rem;
        margin-top: 12px;
        font-weight: 600;
    }

    /* ---- Stat / toolbar row ---- */
    .stat-row {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 4px;
    }
    .stat-chip {
        background: var(--secondary-background-color);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 10px 16px;
        font-size: 0.9rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    }
    .stat-chip b { color: #b794f6; font-size: 1.05rem; }

    /* ---- Post cards ---- */
    .post-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 24px 26px;
        margin-bottom: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.45);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .post-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 26px rgba(0,0,0,0.6);
    }
    .post-title {
        color: var(--text-color);
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    .post-meta {
        color: #9aa3b2;
        font-size: 0.85rem;
        margin-bottom: 14px;
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        align-items: center;
    }
    .post-meta .author-badge {
        background: rgba(139,92,246,0.18);
        color: #c4b5fd;
        padding: 2px 10px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .post-content {
        color: var(--text-color);
        opacity: 0.9;
        line-height: 1.65;
        white-space: pre-wrap;
    }

    /* ---- Comments ---- */
    .comment-box {
        background: rgba(255,255,255,0.04);
        border-left: 3px solid #8b5cf6;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .comment-author { font-weight: 600; color: #c4b5fd; font-size: 0.88rem; }
    .comment-date { color: #8b93a5; font-size: 0.75rem; margin-left: 8px; }
    .comment-text { color: var(--text-color); opacity: 0.9; margin-top: 4px; font-size: 0.92rem; }

    .section-label {
        color: #c7ccd6;
        font-weight: 700;
        font-size: 0.95rem;
        margin: 6px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* ---- Buttons ---- */
    .stButton>button {
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 8px 18px;
        transition: all 0.2s;
    }

    /* Sidebar tweaks */
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Session State Management
# ------------------------------------------------------------------
def _init_state():
    defaults = {
        "access_token": None,
        "refresh_token": None,
        "username": None,
        "user_id": None,
        "current_page": 1,
        "search_query": "",
        "editing_post_id": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()


# ------------------------------------------------------------------
# JWT helpers (decode without external deps; server still verifies)
# ------------------------------------------------------------------
def _decode_jwt_user_id(token):
    """Return user_id from a SimpleJWT access token (client-side only)."""
    try:
        payload_b64 = token.split(".")[1]
        # pad base64
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("user_id")
    except Exception:
        return None


def get_headers():
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


def _refresh_access():
    """Use the refresh token to obtain a new access token."""
    if not st.session_state.refresh_token:
        return False
    try:
        r = requests.post(
            f"{AUTH_BASE_URL}/token/refresh/",
            json={"refresh": st.session_state.refresh_token},
        )
        if r.status_code == 200:
            st.session_state.access_token = r.json().get("access")
            return True
    except Exception:
        pass
    return False


def api_request(method, url, *, json_body=None, auth=False, retry=True):
    """
    Wrapper around requests that:
      - attaches the bearer token if auth=True
      - transparently refreshes an expired access token once
    Returns (response, error_message).
    """
    headers = get_headers() if auth else {}
    try:
        r = requests.request(method, url, json=json_body, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    # If access token expired, refresh and retry once
    if r.status_code == 401 and auth and retry:
        if _refresh_access():
            return api_request(method, url, json_body=json_body, auth=auth, retry=False)
    return r, None


# ------------------------------------------------------------------
# Authentication actions
# ------------------------------------------------------------------
def do_login(username, password):
    try:
        r = requests.post(
            f"{AUTH_BASE_URL}/login/",
            json={"username": username, "password": password},
            timeout=10,
        )
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return False
    if r.status_code == 200:
        data = r.json()
        st.session_state.access_token = data.get("access")
        st.session_state.refresh_token = data.get("refresh")
        st.session_state.username = username
        st.session_state.user_id = _decode_jwt_user_id(data.get("access"))
        return True
    st.error("Invalid credentials. Please check your username and password.")
    return False


def do_register(username, password, password2, email):
    payload = {"username": username, "password": password, "password2": password2}
    if email:
        payload["email"] = email
    try:
        r = requests.post(f"{AUTH_BASE_URL}/register/", json=payload, timeout=10)
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return False
    if r.status_code == 201:
        st.success("✅ Registration successful! You can log in now.")
        return True
    try:
        detail = r.json()
    except Exception:
        detail = r.text
    st.error(f"Registration failed: {detail}")
    return False


def do_logout():
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.editing_post_id = None


# ------------------------------------------------------------------
# Post actions
# ------------------------------------------------------------------
def fetch_posts(page=1, search=""):
    params = {"page": page, "page_size": 10}
    if search:
        params["search"] = search
    try:
        r = requests.get(f"{API_BASE_URL}/posts/", params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return [], 0, None, None
    if r.status_code == 200:
        data = r.json()
        results = data.get("results", []) if isinstance(data, dict) else data
        count = data.get("count", len(results)) if isinstance(data, dict) else len(results)
        return results, count, data.get("next"), data.get("previous")
    st.error(f"Failed to fetch posts (HTTP {r.status_code}).")
    return [], 0, None, None


def create_post(title, content):
    r, err = api_request(
        "POST", f"{API_BASE_URL}/posts/",
        json_body={"title": title, "content": content}, auth=True,
    )
    if err:
        st.error(err)
        return False
    if r.status_code == 201:
        st.success("🎉 Post published!")
        return True
    st.error(f"Failed to create post: {r.text}")
    return False


def update_post(post_id, title, content):
    r, err = api_request(
        "PATCH", f"{API_BASE_URL}/posts/{post_id}/",
        json_body={"title": title, "content": content}, auth=True,
    )
    if err:
        st.error(err)
        return False
    if r.status_code == 200:
        st.success("✅ Post updated!")
        return True
    st.error(f"Failed to update post: {r.text}")
    return False


def delete_post(post_id):
    r, err = api_request(
        "DELETE", f"{API_BASE_URL}/posts/{post_id}/", json_body=None, auth=True,
    )
    if err:
        st.error(err)
        return False
    if r.status_code in (200, 204):
        st.success("🗑️ Post deleted.")
        return True
    st.error(f"Failed to delete post: {r.text}")
    return False


# ------------------------------------------------------------------
# Comment actions
# ------------------------------------------------------------------
def fetch_comments(post_id):
    try:
        r = requests.get(
            f"{API_BASE_URL}/posts/{post_id}/comments/?page_size=100", timeout=10
        )
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch comments: {e}")
        return []
    if r.status_code == 200:
        data = r.json()
        return data.get("results", []) if isinstance(data, dict) else data
    return []


def create_comment(post_id, text):
    r, err = api_request(
        "POST", f"{API_BASE_URL}/posts/{post_id}/comments/",
        json_body={"text": text}, auth=True,
    )
    if err:
        st.error(err)
        return False
    if r.status_code == 201:
        st.success("💬 Comment added!")
        return True
    st.error(f"Failed to add comment: {r.text}")
    return False


def delete_comment(comment_id):
    r, err = api_request(
        "DELETE", f"{API_BASE_URL}/comments/{comment_id}/", json_body=None, auth=True,
    )
    if err:
        st.error(err)
        return False
    if r.status_code in (200, 204):
        st.success("🗑️ Comment deleted.")
        return True
    st.error(f"Failed to delete comment: {r.text}")
    return False


# ------------------------------------------------------------------
# Display helpers
# ------------------------------------------------------------------
def fmt_date(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y · %I:%M %p")
    except Exception:
        return date_str


def author_label(author_id):
    """Author comes back as a bare user ID (no user-list endpoint exists)."""
    if author_id is None:
        return "Unknown"
    if st.session_state.user_id and author_id == st.session_state.user_id:
        return f"{st.session_state.username} (you)"
    return f"User #{author_id}"


def render_header():
    st.markdown("""
    <div class="hero-header">
        <h1>📝 Django Blog</h1>
        <p>Share your stories, ideas, and thoughts with the world.</p>
        <span class="hero-badge">⚡ Powered by Django REST Framework</span>
    </div>
    """, unsafe_allow_html=True)


def render_post_card(post):
    post_id = post.get("id")
    author_id = post.get("author")
    is_author = (
        st.session_state.user_id is not None
        and author_id == st.session_state.user_id
    )

    date_str = fmt_date(post.get("created_at", ""))

    st.markdown(f"""
    <div class="post-card">
        <h3 class="post-title">{post.get('title', 'Untitled')}</h3>
        <div class="post-meta">
            <span class="author-badge">👤 {author_label(author_id)}</span>
            <span>📅 {date_str}</span>
        </div>
        <div class="post-content">{post.get('content', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons row (only for the post's author)
    if is_author:
        cols = st.columns([1, 1, 6])
        with cols[0]:
            if st.button("✏️ Edit", key=f"edit_btn_{post_id}"):
                st.session_state.editing_post_id = post_id
                st.rerun()
        with cols[1]:
            if st.button("🗑️ Delete", key=f"del_btn_{post_id}"):
                if delete_post(post_id):
                    st.rerun()

    # Comments section (expandable)
    with st.expander("💬 View / Add Comments", expanded=False):
        render_comments_section(post_id)


def render_comments_section(post_id):
    comments = fetch_comments(post_id)

    st.markdown(f"""
    <div class="section-label">💬 {len(comments)} comment{'s' if len(comments) != 1 else ''}</div>
    """, unsafe_allow_html=True)

    if not comments:
        st.info("No comments yet. Be the first to share your thoughts!")

    for c in comments:
        c_author_id = c.get("author")
        is_comment_author = (
            st.session_state.user_id is not None
            and c_author_id == st.session_state.user_id
        )
        st.markdown(f"""
        <div class="comment-box">
            <span class="comment-author">{author_label(c_author_id)}</span>
            <span class="comment-date">{fmt_date(c.get('created_at', ''))}</span>
            <div class="comment-text">{c.get('text', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        if is_comment_author:
            if st.button("🗑️ Delete my comment", key=f"del_cmt_{c.get('id')}"):
                if delete_comment(c.get("id")):
                    st.rerun()

    # Add comment form
    st.markdown('<div class="section-label">✍️ Leave a comment</div>', unsafe_allow_html=True)
    if st.session_state.access_token:
        with st.form(f"comment_form_{post_id}", clear_on_submit=True):
            comment_text = st.text_area(
                "Your comment", key=f"comment_input_{post_id}", height=100,
                label_visibility="collapsed",
                placeholder="Write a comment...",
            )
            submitted = st.form_submit_button("Post Comment")
            if submitted:
                if comment_text.strip():
                    if create_comment(post_id, comment_text.strip()):
                        st.rerun()
                else:
                    st.warning("Comment cannot be empty.")
    else:
        st.markdown("🔒 **Log in** from the sidebar to leave a comment.")


# ------------------------------------------------------------------
# SIDEBAR — Authentication + Create / Edit Post
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🔑 Account")

    if st.session_state.access_token:
        st.success(f"Logged in as\n**{st.session_state.username}**")
        if st.button("🚪 Logout", use_container_width=True):
            do_logout()
            st.rerun()

        st.markdown("---")

        # Create OR Edit post form
        if st.session_state.editing_post_id:
            st.markdown("### ✏️ Edit Post")
            # fetch the post being edited
            try:
                pr = requests.get(
                    f"{API_BASE_URL}/posts/{st.session_state.editing_post_id}/", timeout=10
                )
                editing_post = pr.json() if pr.status_code == 200 else {}
            except Exception:
                editing_post = {}

            with st.form("edit_post_form"):
                e_title = st.text_input("Title", value=editing_post.get("title", ""))
                e_content = st.text_area("Content", value=editing_post.get("content", ""))
                col_a, col_b = st.columns(2)
                with col_a:
                    save = st.form_submit_button("💾 Save", use_container_width=True)
                with col_b:
                    cancel = st.form_submit_button("↩️ Cancel", use_container_width=True)
                if save:
                    if e_title.strip() and e_content.strip():
                        if update_post(st.session_state.editing_post_id, e_title.strip(), e_content.strip()):
                            st.session_state.editing_post_id = None
                            st.rerun()
                    else:
                        st.warning("Both fields are required.")
                if cancel:
                    st.session_state.editing_post_id = None
                    st.rerun()
        else:
            st.markdown("### 📝 Create New Post")
            with st.form("create_post_form"):
                n_title = st.text_input("Title")
                n_content = st.text_area("Content", height=150)
                submit_post = st.form_submit_button("🚀 Publish Post", use_container_width=True)
                if submit_post:
                    if n_title.strip() and n_content.strip():
                        if create_post(n_title.strip(), n_content.strip()):
                            st.rerun()
                    else:
                        st.warning("Please fill in both title and content.")
    else:
        auth_mode = st.radio("Choose action", ["Login", "Register"], horizontal=True)

        if auth_mode == "Login":
            with st.form("login_form"):
                l_username = st.text_input("Username")
                l_password = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if l_username and l_password:
                        if do_login(l_username, l_password):
                            st.rerun()
                    else:
                        st.warning("Enter username and password.")
        else:
            with st.form("register_form"):
                r_username = st.text_input("Username")
                r_email = st.text_input("Email (optional)")
                r_password = st.text_input("Password (min 8 chars)", type="password")
                r_password2 = st.text_input("Confirm password", type="password")
                if st.form_submit_button("Register", use_container_width=True):
                    if not (r_username and r_password and r_password2):
                        st.warning("Username, password and confirmation are required.")
                    elif r_password != r_password2:
                        st.warning("Passwords do not match.")
                    elif len(r_password) < 8:
                        st.warning("Password must be at least 8 characters.")
                    else:
                        do_register(r_username, r_password, r_password2, r_email)

    st.markdown("---")
    st.caption("Backend: `http://127.0.0.1:8000`")


# ------------------------------------------------------------------
# MAIN CONTENT
# ------------------------------------------------------------------
render_header()

# Toolbar: search + stats
posts, total, next_url, prev_url = fetch_posts(
    st.session_state.current_page, st.session_state.search_query
)

search_col, stat_col = st.columns([3, 2])
with search_col:
    with st.form("search_form", clear_on_submit=False):
        s_cols = st.columns([5, 1])
        new_search = s_cols[0].text_input(
            "🔍 Search posts", value=st.session_state.search_query,
            placeholder="Search by title or content...",
            label_visibility="collapsed",
        )
        if s_cols[1].form_submit_button("Search", use_container_width=True):
            st.session_state.search_query = new_search.strip()
            st.session_state.current_page = 1
            st.rerun()
with stat_col:
    st.markdown("""
    <div class="stat-row">
        <div class="stat-chip">📰 <b>{}</b> posts total</div>
    </div>
    """.format(total), unsafe_allow_html=True)

# Reset page button if searching
if st.session_state.search_query:
    if st.button("✖️ Clear search"):
        st.session_state.search_query = ""
        st.session_state.current_page = 1
        st.rerun()

st.markdown("")

# Posts list
if not posts:
    st.warning(
        "⚠️ No posts found. Make sure your Django server is running on "
        "`http://127.0.0.1:8000`."
    )
else:
    st.markdown(f"#### 📰 Posts {f'· Page {st.session_state.current_page}' if total > 10 else ''}")
    for post in posts:
        render_post_card(post)

    # Pagination controls
    if total > 10:
        st.markdown("---")
        p_cols = st.columns([1, 2, 1])
        with p_cols[0]:
            if st.button("⬅️ Previous", disabled=(prev_url is None), use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
        with p_cols[1]:
            st.markdown(
                f"<div style='text-align:center;color:#9aa3b2;padding-top:8px;'>"
                f"Page <b>{st.session_state.current_page}</b></div>",
                unsafe_allow_html=True,
            )
        with p_cols[2]:
            if st.button("Next ➡️", disabled=(next_url is None), use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()
