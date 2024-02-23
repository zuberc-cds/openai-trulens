import streamlit as st
from utils import create_sidebar
from constant import IMAGE_PATH

def get_conversation_data():
    """
    Get conversation data from session state.
    """
    if "selected_chat" not in st.session_state:
        return None
    return st.session_state.selected_chat

def show_chat_messages(conversation_data):
    """
    Show chat messages and details for the conversation.
    """
    if not conversation_data:
        st.title("No chat selected")
        return
    # Display details for the conversation
    id_rating_col, desc_col = st.columns([3, 7])
    with id_rating_col:
        st.markdown(f"**Chat ID:** {conversation_data['id']}")
        st.markdown(f"**Rating:** {conversation_data['rating']}")
    with desc_col:
        st.markdown(f"**Description:** {conversation_data['description']}")
    st.markdown("---")
    for msg in conversation_data["messages"]:
        content = msg["content"]
        if IMAGE_PATH in content:
            st.image(content)
        else:
            st.chat_message(msg["role"]).write(msg["content"])

####### start
create_sidebar()
conversation_data = get_conversation_data()
show_chat_messages(conversation_data)