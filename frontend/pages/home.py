import streamlit as st
from frontend import api, components

def render():
    
    # Top Friends bar
    my_id = st.session_state.user_id
    following = api.fetch_following(my_id) if my_id else []
    
    if following:
        components.render_friends_bar(following)
    else:
        st.info("You aren't following anyone yet. Head to Explore to find people!")
        
    st.markdown("---")
    
    # Feed
    posts, total, next_u, prev_u = api.fetch_posts(page=st.session_state.get('home_page', 1), endpoint="/feed/")
    
    if not posts:
        st.markdown("<h4 style='text-align: center; color: #9aa3b2; margin-top: 40px;'>No posts in your feed yet.</h4>", unsafe_allow_html=True)
    else:
        for p in posts:
            components.render_post_card(p, is_author=(p.get('author') == my_id))
            
        # Pagination
        if total > 10:
            c1, c2, c3 = st.columns([1,2,1])
            with c1:
                if st.button("Previous", disabled=(prev_u is None), key="hp_prev"):
                    st.session_state.home_page = st.session_state.get('home_page', 1) - 1
                    st.rerun()
            with c2:
                st.markdown(f"<div style='text-align:center;'>Page {st.session_state.get('home_page', 1)}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("Next", disabled=(next_u is None), key="hp_next"):
                    st.session_state.home_page = st.session_state.get('home_page', 1) + 1
                    st.rerun()
