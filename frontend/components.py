import streamlit as st
import hashlib
from frontend import api

def clean_html(text):
    return " ".join(line.strip() for line in text.splitlines())

def get_avatar_color(username):
    hash_obj = hashlib.md5((username or "unknown").encode())
    hue = int(hash_obj.hexdigest()[:4], 16) % 360
    return f"hsl({hue}, 70%, 40%)"

def render_avatar(username, size=40):
    initial = (username[0] if username else "?").upper()
    color = get_avatar_color(username)
    return clean_html(f'''
    <div style="width: {size}px; height: {size}px; border-radius: 50%; background-color: {color}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: {size//2}px;">
        {initial}
    </div>
    ''')

def render_friends_bar(friends):
    if not friends: return
    
    st.html('<div class="friends-bar-container">')
    cols = st.columns(len(friends))
    for i, friend in enumerate(friends):
        with cols[i]:
            username = friend.get("username", "Unknown")
            st.html(clean_html(f'''
            <div class="avatar-container" title="{username}">
                <div class="avatar-circle" style="border-color: {get_avatar_color(username)};">
                    {(username[0] if username else "?").upper()}
                </div>
                <div class="avatar-label">{username}</div>
            </div>
            '''))
            if st.button("View", key=f"fbar_{friend['id']}", help=f"View {username}", use_container_width=True):
                st.session_state.viewing_user_id = friend['id']
                st.session_state.current_page = "Profile"
                st.rerun()
    st.html('</div>')


def fmt_date(date_str):
    if not date_str: return ""
    import datetime
    try:
        dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d · %I:%M %p")
    except Exception:
        return date_str

def render_post_card(post, is_author=False):
    post_id = post.get("id")
    author_username = post.get("author_username", "Unknown")
    author_id = post.get("author")
    
    st.html(clean_html(f'''
    <div class="post-card">
        <div class="post-header">
            {render_avatar(author_username, 40)}
            <div class="post-header-info">
                <span class="post-author">{author_username}</span>
                <span class="post-date">{fmt_date(post.get('created_at', ''))}</span>
            </div>
        </div>
        <h4 style="margin: 0 0 8px 0; color: var(--text-color);">{post.get('title', '')}</h4>
        <div class="post-content">{post.get('content', '')}</div>
    </div>
    '''))

    # Actions
    col1, col2, col3, col4 = st.columns([2,2,2,4])
    
    # Like
    like_label = f"❤️ {post.get('like_count', 0)}" if post.get('is_liked') else f"🤍 {post.get('like_count', 0)}"
    with col1:
        if st.button(like_label, key=f"like_{post_id}", disabled=not post.get('can_like', True)):
            if not st.session_state.access_token:
                st.warning("Log in to like")
            else:
                if api.toggle_like(post_id, post.get('is_liked')):
                    st.rerun()
                    
    # Save
    save_label = "🔖 Saved" if post.get('is_saved') else "📑 Save"
    with col2:
        if st.button(save_label, key=f"save_{post_id}"):
            if not st.session_state.access_token:
                st.warning("Log in to save")
            else:
                if api.toggle_save(post_id, post.get('is_saved')):
                    st.rerun()
                    
    # Comment count indicator
    with col3:
        st.button(f"💬 {post.get('comment_count', 0)}", key=f"cc_{post_id}", disabled=True)

    with col4:
        # Profile link for non-author
        if st.session_state.user_id != author_id:
            if st.button(f"👤 View {author_username}", key=f"prof_{post_id}", use_container_width=True):
                st.session_state.viewing_user_id = author_id
                st.session_state.current_page = "Profile"
                st.rerun()
        elif is_author:
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                if st.button("✏️", key=f"edit_{post_id}"):
                    st.session_state.editing_post_id = post_id
                    st.rerun()
            with subcol2:
                if st.button("🗑️", key=f"del_{post_id}"):
                    if api.delete_post(post_id):
                        st.rerun()

    # Comments expander
    with st.expander("Comments"):
        render_comments(post)

def render_comments(post):
    post_id = post.get('id')
    post_author_id = post.get('author')
    comments = api.fetch_comments(post_id)
    
    for c in comments:
        c_author_id = c.get('author')
        can_delete = (st.session_state.user_id == c_author_id) or (st.session_state.user_id == post_author_id)
        
        st.html(clean_html(f'''
        <div class="comment-box">
            <div class="comment-header">
                {render_avatar(c.get('author_username'), 24)}
                <span class="comment-author">{c.get('author_username', 'Unknown')}</span>
                <span class="comment-date">{fmt_date(c.get('created_at', ''))}</span>
            </div>
            <div class="comment-text">{c.get('text', '')}</div>
        </div>
        '''))
        if can_delete:
            if st.button("🗑️ Delete", key=f"delcmt_{c.get('id')}"):
                if api.delete_comment(c.get('id')):
                    st.rerun()

    if post.get('can_comment', True) and st.session_state.access_token:
        with st.form(f"add_comment_{post_id}", clear_on_submit=True):
            text = st.text_input("Add a comment...", label_visibility="collapsed")
            if st.form_submit_button("Post"):
                if text.strip():
                    if api.create_comment(post_id, text.strip()):
                        st.rerun()
    elif not st.session_state.access_token:
        st.info("Log in to comment")
    else:
        st.info("Comments disabled by author")


def render_user_card(user, key_prefix=""):
    st.html(clean_html(f'''
    <div class="user-card">
        {render_avatar(user.get("username"), 48)}
        <div class="user-card-info">
            <h4 class="user-card-name">{user.get("username", "Unknown")}</h4>
            <p class="user-card-stats">Followers: {user.get("follower_count", 0)} · Following: {user.get("following_count", 0)}</p>
        </div>
    </div>
    '''))
    
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("View Profile", key=f"{key_prefix}vp_{user['id']}", use_container_width=True):
            st.session_state.viewing_user_id = user['id']
            st.session_state.current_page = "Profile"
            st.rerun()
    with col2:
        if st.session_state.access_token and user['id'] != st.session_state.user_id:
            is_following = user.get("is_following", False)
            btn_label = "Unfollow" if is_following else "Follow"
            if st.button(btn_label, key=f"{key_prefix}flw_{user['id']}", use_container_width=True):
                if api.toggle_follow(user['id'], is_following):
                    st.rerun()
