import streamlit as st
from frontend import api

def render():
    st.title("Settings")
    
    profile = api.fetch_my_profile()
    if not profile:
        st.error("Could not load profile settings.")
        return
        
    st.subheader("Profile Information")
    with st.form("settings_form"):
        bio = st.text_area("Bio", value=profile.get('bio', ''))
        
        st.subheader("Privacy")
        st.write("Control who can interact with your posts.")
        
        opts = {
            "everyone": "Everyone",
            "friends": "Friends only (mutual follows)",
            "nobody": "Nobody"
        }
        idx_likes = list(opts.keys()).index(profile.get('allow_likes_from', 'everyone'))
        idx_comments = list(opts.keys()).index(profile.get('allow_comments_from', 'everyone'))
        
        allow_likes = st.selectbox("Who can like your posts?", options=list(opts.keys()), format_func=lambda x: opts[x], index=idx_likes)
        allow_comments = st.selectbox("Who can comment on your posts?", options=list(opts.keys()), format_func=lambda x: opts[x], index=idx_comments)
        
        if st.form_submit_button("Save Settings"):
            if api.update_my_profile(bio, allow_likes, allow_comments):
                st.rerun()
