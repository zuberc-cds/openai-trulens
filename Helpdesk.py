import streamlit as st
import os
from constant import *
from image_operations import encode_image
from openai_chat import OpenAIChat
from utils import get_logger, create_sidebar
from chat_data import handle_chat_data_storage
import streamlit.components.v1 as components


logger = get_logger()


def get_image_file_path(image_file):
    """
    Get the file path and type of the given image file.

    Parameters:
    - image_file: The image file to process.

    Returns:
    - file_path: The path of the processed image file.
    - file_type: The type of the image file.
    """
    file_path = file_type = None
    if image_file:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir + IMAGE_PATH, image_file.name)
        file_type = image_file.type
        with open(file_path, "wb") as file:
            file.write(image_file.read())
        logger.info(f"writing image to File path: {file_path}")
    return file_path, file_type


def change_button_colour(widget_label, font_color, background_color='transparent'):
    htmlstr = f"""
        <script>
            var elements = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < elements.length; ++i) {{ 
                if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.color ='{font_color}';
                    elements[i].style.background = '{background_color}'
                }}
            }}
        </script>
        """
    components.html(f"{htmlstr}", height=0, width=0)

def reset_session_state():
    """
    Reset the session state.
    """
    st.session_state.clear()
    st.rerun()


def handle_image_content(file_path):
    """
    Handle the image content and return the encoded image contents.

    Args:
        file_path: The path to the image file.

    Returns:
        The base64 encoded image contents.
    """
    image_contents = encode_image(file_path)
    logger.info("encoded image contents")
    return image_contents


def handle_historical_chat_data():
    """
    Function to handle historical chat data.
    """
    for msg in st.session_state.messages:
        content = msg["content"]
        role = msg["role"]
        if IMAGE_PATH in content:
            st.chat_message(role).image(content)
        else:
            st.chat_message(role).write(content)


def handle_rating_value():
    """
    Handle the rating value and button clicks for thumbs up, thumbs down, and save chat.
    """
    thumbs_up_col, thumbs_down_col, save_chat_col = st.columns([1.5, 3.5, 5])
    rating = st.session_state.rating
    with thumbs_up_col:
        thumbs_up = st.button("👍", key="thumbs_up")
    with thumbs_down_col:
        thumbs_down = st.button("👎", key="thumbs_down")
    with save_chat_col:
        save_chat = st.button("End Session", key="end_session")
        change_button_colour("End Session", "white", "green")
        if save_chat:
            handle_chat_data_storage()
            reset_session_state()

    if thumbs_up:
        rating = "👍"
    if thumbs_down:
        rating = "👎"
    return rating


def feedback_ui_thumbs():
    """
    Generate the feedback UI for thumbs and handle the rating value.
    """
    feed_sec, rating_sec = st.columns([5, 5])
    with feed_sec:
        st.markdown("#### 📝 Feedback")

    if "rating" not in st.session_state:
        st.session_state.rating = "👍"
    rating = handle_rating_value()
    st.session_state.rating = rating
    with rating_sec:
        st.markdown(f"#### {st.session_state.rating}")


def chat_feedback_section():
    """
    Function for creating a chat feedback section with columns for chat and feedback UI.
    """
    chat_col, feedback_col = st.columns([8, 3])
    with chat_col:
        st.title("💬 IT SmartSupport Agent - SolvIT")
        st.caption("🚀 Chatbot Powered by OpenAI")
    with feedback_col:
        feedback_ui_thumbs()


def get_openai_chat_instance():
    """
    Function to get an instance of the OpenAIChat class,
    creating a new instance if it does not exist in the session state.
    Returns the OpenAIChat instance.
    """
    if "openai_chat" not in st.session_state:
        st.session_state["openai_chat"] = OpenAIChat()
    return st.session_state.openai_chat


def image_uploaded():
    """
    Get the recent image object from the session state.

    Returns:
        The recent image object if it exists in the session state, otherwise None.
    """
    if "image_key" in st.session_state and st.session_state["image_key"] is not None:
        st.session_state.image_uploaded = st.session_state["image_key"]

        # get the file path and type
        file_path, file_type = get_image_file_path(st.session_state.image_uploaded)
        # st.session_state.messages.append({"role": "user", "content": file_path})
        st.session_state["file_path"] = file_path
        st.session_state["file_type"] = file_type


def handle_on_submit(chat_container, prompt=DEFAULT_USER_QUERY):
    openAIChatInst = get_openai_chat_instance()
    image_contents = None
    with chat_container:
        st.chat_message("user").write(prompt)
        if "file_path" in st.session_state:
            # image content is the base64 encoded image
            st.session_state.messages.append({"role": "user", "content": st.session_state.file_path})
            image_contents = handle_image_content(st.session_state.file_path)
            st.chat_message("user").image(st.session_state.file_path)

        if image_contents:
            response = openAIChatInst.start_image_processing(
                image_contents, prompt, st.session_state.file_type
            )
            # remove the file path and type from the session state
            del st.session_state.file_path
            del st.session_state.file_type
            del st.session_state.image_uploaded
        else:
            response = openAIChatInst.ask_and_respond(prompt)
        msg = "".join(list(response.response_gen))
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

def chatbox_func():
    """
    Function to handle the chatbox functionality,
    including processing user input, handling image content, and generating assistant responses.
    """
    chat_feedback_section()
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": WELCOME_MESSAGE}
        ]
    file_handler()
    chat_container = st.container(height=500)
    with chat_container:
        handle_historical_chat_data()

    if prompt := st.chat_input(placeholder="Message SolvIT...", key="input_text"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        handle_on_submit(chat_container, prompt)
        
def button_click_callback():
    if "submit_button" in st.session_state and st.session_state["submit_button"] is not None:
        st.session_state.submit_button_clicked = st.session_state.submit_button

def file_handler():
    _ = st.file_uploader(
        "Upload an Image",
        type=["jpg", "png", "jpeg"],
        key="image_key",
        on_change=image_uploaded,
    )


def page_setup():
    # Custom header
    st.set_page_config(layout="wide")
    create_sidebar()


def start():
    page_setup()
    chatbox_func()


############ - start

start()
