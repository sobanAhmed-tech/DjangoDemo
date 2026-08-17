import streamlit as st
from frontend import api, components

def render():
    st.title("Saved Posts")
    
    posts, total, next_u, prev_u = api.fetch_saved_posts(page=st.session_state.get('saved_page', 1))
    
    if not posts:
        st.info("You haven't saved any posts yet.")
    else:
        for p in posts:
            components.render_post_card(p)
            
        if total > 10:
            c1, c2, c3 = st.columns([1,2,1])
            with c1:
                if st.button("Previous", disabled=(prev_u is None), key="sp_prev"):
                    st.session_state['saved_page'] = st.session_state.get('saved_page', 1) - 1
                    st.rerun()
            with c2:
                st.markdown(f"<div style='text-align:center;'>Page {st.session_state.get('saved_page', 1)}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("Next", disabled=(next_u is None), key="sp_next"):
                    st.session_state['saved_page'] = st.session_state.get('saved_page', 1) + 1
                    st.rerun()
