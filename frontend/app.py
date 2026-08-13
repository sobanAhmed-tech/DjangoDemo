import streamlit as st
from frontend import state, api, styles
from frontend.pages import home, explore, profile, notifications, settings

def render_sidebar():
    with st.sidebar:
        st.title("Instagram Clone")
        
        if st.session_state.access_token:
            st.success(f"Logged in as **{st.session_state.username}**")
            
            nav_options = ["Home", "Explore", "Notifications", "Profile", "Settings"]
            for opt in nav_options:
                if st.button(f"{'➡️ ' if st.session_state.current_page == opt else ''}{opt}", use_container_width=True):
                    if opt == "Profile":
                        st.session_state.viewing_user_id = st.session_state.user_id
                    st.session_state.current_page = opt
                    st.rerun()

            st.markdown("---")
            st.markdown("### 📝 New Post")
            with st.form("new_post"):
                title = st.text_input("Title")
                content = st.text_area("Content", height=100)
                if st.form_submit_button("Post", use_container_width=True):
                    if title.strip() and content.strip():
                        if api.create_post(title, content):
                            st.session_state.current_page = "Home"
                            st.rerun()
            
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                api.do_logout()
                st.rerun()
        else:
            mode = st.radio("Welcome", ["Login", "Register"], horizontal=True)
            if mode == "Login":
                with st.form("login"):
                    u = st.text_input("Username")
                    p = st.text_input("Password", type="password")
                    if st.form_submit_button("Login"):
                        if u and p and api.do_login(u, p):
                            st.rerun()
            else:
                with st.form("register"):
                    u = st.text_input("Username")
                    e = st.text_input("Email (optional)")
                    p = st.text_input("Password (min 8 chars)", type="password")
                    p2 = st.text_input("Confirm Password", type="password")
                    if st.form_submit_button("Register"):
                        if u and p and p==p2:
                            api.do_register(u, p, p2, e)
                        else:
                            st.error("Please fill correctly.")

def run():
    state.init_state()
    styles.apply_styles()
    render_sidebar()
    
    page = st.session_state.current_page
    
    if page == "Home":
        if st.session_state.access_token:
            home.render()
        else:
            st.info("Log in to see your home feed.")
            explore.render() # Show explore by default
    elif page == "Explore":
        explore.render()
    elif page == "Profile":
        if st.session_state.access_token:
            profile.render()
        else:
            st.warning("Log in to view profiles.")
    elif page == "Notifications":
        if st.session_state.access_token:
            notifications.render()
        else:
            st.warning("Log in to view notifications.")
    elif page == "Settings":
        if st.session_state.access_token:
            settings.render()
        else:
            st.warning("Log in to view settings.")
