import streamlit as st
from ui.utils.session_state import initialize_session
from ui.utils.api_client import APIClient

st.set_page_config(
    page_title="Multi-Agent Knowledge Base",
    page_icon="🤖",
    layout="wide"
)

# Initialize
initialize_session()
api = APIClient()

st.title("🤖 Multi-Agent Document Q&A System")
st.markdown("Ask questions across your software documentation with specialized AI agents")
