import streamlit as st
from frontend import api, components

def render():
    st.title("Notifications")
    
    requests = api.fetch_follow_requests()
    if requests:
        st.subheader(f"Follow Requests ({len(requests)})")
        for req in requests:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{req.get('username')}** wants to follow you.")
            with col2:
                if st.button("Accept", key=f"acc_{req['id']}"):
                    if api.respond_follow_request(req['id'], "accept"):
                        st.rerun()
            with col3:
                if st.button("Reject", key=f"rej_{req['id']}"):
                    if api.respond_follow_request(req['id'], "reject"):
                        st.rerun()
        st.markdown("---")
    
    notifications = api.fetch_notifications()
    if not notifications:
        st.info("You don't have any notifications yet.")
        return
        
    unread_count = sum(1 for n in notifications if not n.get('read'))
    if unread_count > 0:
        if st.button(f"Mark all as read ({unread_count})"):
            if api.mark_notifications_read():
                st.rerun()
                
    st.markdown("---")
    
    for n in notifications:
        unread_class = "notification-unread" if not n.get('read') else ""
        actor_name = n.get('actor_username', 'Unknown')
        
        target = f" on '{n.get('post_title')}'" if n.get('post_title') else ""
        text = f"**{actor_name}** {n.get('verb_display', 'interacted with you')}{target}"
        
        html_string = " ".join(line.strip() for line in f'''
        <div class="notification-card {unread_class}">
            {components.render_avatar(actor_name, 40)}
            <div style="flex-grow: 1;">
                <div style="color: var(--text-color); font-size: 0.95rem;">{text}</div>
                <div style="color: #9aa3b2; font-size: 0.75rem;">{components.fmt_date(n.get('created_at', ''))}</div>
            </div>
        </div>
        '''.splitlines())
        st.html(html_string)
