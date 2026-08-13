import streamlit as st
from frontend import app

st.set_page_config(
    page_title="Soban Django Project",
    layout="wide",
    initial_sidebar_state="expanded",
)

if __name__ == "__main__":
    app.run()
