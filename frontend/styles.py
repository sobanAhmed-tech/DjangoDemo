import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
        /* Base app background */
        .stApp {
            background-color: var(--background-color);
        }

        /* Top Friends Bar / Avatars */
        .friends-bar-container {
            display: flex;
            gap: 16px;
            overflow-x: auto;
            padding: 10px 0;
            margin-bottom: 24px;
        }
        .friends-bar-container::-webkit-scrollbar {
            height: 6px;
        }
        .friends-bar-container::-webkit-scrollbar-thumb {
            background-color: rgba(255,255,255,0.2);
            border-radius: 4px;
        }
        .avatar-circle {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: white;
            flex-shrink: 0;
            border: 2px solid #8b5cf6;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .avatar-circle:hover {
            transform: scale(1.05);
        }
        .avatar-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            cursor: pointer;
        }
        .avatar-label {
            font-size: 0.75rem;
            color: var(--text-color);
            max-width: 64px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            text-align: center;
        }

        /* Post Cards */
        .post-card {
            background: var(--secondary-background-color);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.2);
        }
        .post-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        .post-header-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 16px;
        }
        .post-header-info {
            display: flex;
            flex-direction: column;
        }
        .post-author {
            font-weight: 600;
            font-size: 0.95rem;
            color: var(--text-color);
        }
        .post-date {
            font-size: 0.75rem;
            color: #9aa3b2;
        }
        .post-content {
            color: var(--text-color);
            line-height: 1.5;
            white-space: pre-wrap;
            margin-bottom: 16px;
            font-size: 0.95rem;
        }
        
        /* Action Row */
        .action-row {
            display: flex;
            gap: 16px;
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 12px;
            margin-top: 12px;
        }

        /* User Cards (Explore / Follow List) */
        .user-card {
            background: var(--secondary-background-color);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 12px;
        }
        .user-card-info {
            flex-grow: 1;
        }
        .user-card-name {
            font-weight: bold;
            font-size: 1rem;
            margin: 0;
            color: var(--text-color);
        }
        .user-card-stats {
            font-size: 0.8rem;
            color: #9aa3b2;
            margin: 4px 0 0 0;
        }

        /* Notification Card */
        .notification-card {
            background: var(--secondary-background-color);
            border-left: 4px solid #8b5cf6;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .notification-unread {
            border-left-color: #ef4444;
            background: rgba(239, 68, 68, 0.05);
        }
        
        /* Comments */
        .comment-box {
            background: rgba(255,255,255,0.04);
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
        }
        .comment-header {
            display: flex;
            gap: 8px;
            align-items: baseline;
            margin-bottom: 4px;
        }
        .comment-author {
            font-weight: 600;
            color: #c4b5fd;
            font-size: 0.85rem;
        }
        .comment-date {
            color: #8b93a5;
            font-size: 0.7rem;
        }
        .comment-text {
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)
