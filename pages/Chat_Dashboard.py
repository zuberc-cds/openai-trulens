import streamlit as st
from utils import create_sidebar
from chat_data import get_chat_data



def load_chat_details(chat):
    """
    Load chat details into the session state and switch to the Chat Details page.
    """
    st.session_state.selected_chat = chat
    st.switch_page("./pages/Chat_Details.py")

def build_alert_headers():
    """
    Function to build alert headers for chat ID, rating, and action.
    """
    chat_id_col, chat_desc_col, rating_col, action_col = st.columns([1,6,1,2])
    with chat_id_col:
        st.markdown("**Chat ID**")
    with chat_desc_col:
        st.markdown("**Description**")
    with rating_col:
        st.markdown("**Rating**")
    with action_col:
        st.markdown("**Action**")

    # Insert a visual separator (line) after the headers
    st.markdown(
        "<hr style='margin-top:0.25rem; margin-bottom:0.25rem;'/>",
        unsafe_allow_html=True,
    )

def create_chat_table():
    """
    Display the chat data in a table format with buttons for actions.

    This function retrieves chat data, builds the alert headers,
    and displays the chat data in a table format with buttons for actions.
    """
    # Retrieve chat data
    chat_data = get_chat_data()

    # Build alert headers
    build_alert_headers()

    # If no chat data, display a message and return
    if not chat_data:
        st.title("No Chats Found")
        return

    # Display chat data in a table format with buttons for actions
    for chat in chat_data:
        chat_id_col, desc_col, rating_col, action_col = st.columns([1,6,1,2])
        with chat_id_col:
            st.write(chat["id"])
        with desc_col:
            st.write(chat["description"])
        with rating_col:
            st.write(chat["rating"])

        do_action = action_col.button("View Details", key=chat["id"])
        if do_action:
            load_chat_details(chat)
        # Insert a visual separator (line) after each row
        st.markdown(
            "<hr style='margin-top:0.25rem; margin-bottom:0.25rem;'/>",
            unsafe_allow_html=True,
        )

######### start
create_sidebar()
create_chat_table()