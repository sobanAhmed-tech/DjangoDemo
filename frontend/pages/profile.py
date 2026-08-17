import streamlit as st
from frontend import api, components

def render():
    user_id = st.session_state.viewing_user_id
    if not user_id:
        st.error("No user selected.")
        return
        
    profile = api.fetch_user_profile(user_id)
    if not profile:
        st.error("Failed to load profile.")
        return
    
    is_me = (user_id == st.session_state.user_id)
    
    st.markdown(f"## {components.render_avatar(profile.get('username'), 64)} {profile.get('username')}", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**Bio**: {profile.get('bio', 'No bio provided.')}")
        
    with col2:
        if is_me:
            if st.button("Edit Profile", use_container_width=True):
                st.session_state.current_page = "Settings"
                st.rerun()
        else:
            is_following = profile.get('is_following', False)
            has_pending = profile.get('has_pending_request', False)
            
            if has_pending:
                if st.button("Requested (Cancel)", use_container_width=True):
                    if api.toggle_follow(user_id, True):
                        st.rerun()
            else:
                if st.button("Unfollow" if is_following else "Follow", use_container_width=True):
                    if api.toggle_follow(user_id, is_following):
                        st.rerun()
                    
    # Stats
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Posts", profile.get("post_count", 0))
    sc2.metric("Followers", profile.get("follower_count", 0))
    sc3.metric("Following", profile.get("following_count", 0))
    
    # Mutuals
    if not is_me:
        mutuals = api.fetch_mutual_friends(user_id)
        if mutuals:
            st.markdown(f"**Mutual Friends ({len(mutuals)})**")
            components.render_friends_bar(mutuals)
            
    st.markdown("---")
    st.subheader(f"Posts by {profile.get('username')}")
    
    posts, total, next_u, prev_u = api.fetch_user_posts(user_id, page=st.session_state.get(f'prof_page_{user_id}', 1))
    if not posts:
        st.info("No posts yet.")
    else:
        for p in posts:
            components.render_post_card(p, is_author=is_me)
            
        if total > 10:
            c1, c2, c3 = st.columns([1,2,1])
            with c1:
                if st.button("Previous", disabled=(prev_u is None), key="pp_prev"):
                    st.session_state[f'prof_page_{user_id}'] = st.session_state.get(f'prof_page_{user_id}', 1) - 1
                    st.rerun()
            with c2:
                st.markdown(f"<div style='text-align:center;'>Page {st.session_state.get(f'prof_page_{user_id}', 1)}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("Next", disabled=(next_u is None), key="pp_next"):
                    st.session_state[f'prof_page_{user_id}'] = st.session_state.get(f'prof_page_{user_id}', 1) + 1
                    st.rerun()
