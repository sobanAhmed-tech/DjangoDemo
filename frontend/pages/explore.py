import streamlit as st
from frontend import api, components

def render():
    st.title("Explore")
    
    tab1, tab2 = st.tabs(["Posts", "People"])
    
    with tab1:
        search_query = st.text_input("🔍 Search Posts...", key="exp_search")
        posts, total, next_u, prev_u = api.fetch_posts(page=st.session_state.get('exp_page', 1), search=search_query)
        
        if not posts:
            st.info("No posts found.")
        else:
            for p in posts:
                components.render_post_card(p, is_author=(p.get('author') == st.session_state.user_id))
                
            if total > 10:
                c1, c2, c3 = st.columns([1,2,1])
                with c1:
                    if st.button("Previous", disabled=(prev_u is None), key="ep_prev"):
                        st.session_state.exp_page = st.session_state.get('exp_page', 1) - 1
                        st.rerun()
                with c2:
                    st.markdown(f"<div style='text-align:center;'>Page {st.session_state.get('exp_page', 1)}</div>", unsafe_allow_html=True)
                with c3:
                    if st.button("Next", disabled=(next_u is None), key="ep_next"):
                        st.session_state.exp_page = st.session_state.get('exp_page', 1) + 1
                        st.rerun()
                        
    with tab2:
        if st.session_state.access_token:
            st.subheader("Suggested For You")
            suggested = api.fetch_suggested_users()
            if suggested:
                for u in suggested:
                    components.render_user_card(u, key_prefix="sug_")
            else:
                st.write("No suggestions at the moment.")
                
            st.markdown("---")
            
        user_search = st.text_input("🔍 Search People...", key="usr_search")
        if user_search:
            users = api.fetch_users(search=user_search)
            if not users:
                st.info("No users found.")
            else:
                for u in users:
                    components.render_user_card(u, key_prefix="search_")
