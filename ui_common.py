import streamlit as st


def show_flash():
    """Show a success message saved before the last page reload."""
    message = st.session_state.pop("flash", None)
    if message:
        st.success(message)


def done(message):
    """Save a message, then reload the page so lists show fresh data."""
    st.session_state["flash"] = message
    st.rerun()
    