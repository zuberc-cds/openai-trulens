import streamlit as st
from utils import get_logger, generate_random_id
from constant import *
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

logger = get_logger()

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def handle_chat_data_storage():
    """
    Handles the storage of conversation data in the chat application.
    """
    if "messages" not in st.session_state:
        return None
    messages = st.session_state["messages"]
    description = get_conversation_description(messages)
    rating = st.session_state["rating"]
    chat_id = generate_random_id()
    conversation_data = {
        "id": chat_id,
        "messages": messages,
        "rating": rating,
        "description": description
    }
    store_update_conversation_data(conversation_data)

def store_update_conversation_data(conversation_data):
    """
    Stores or updates conversation data in the chat data file.
    """
    chat_data = get_chat_data()
    chat_data.append(conversation_data)
    with open(CHAT_DATA_PATH, 'w') as file:
        json.dump(chat_data, file, indent=4)

def get_chat_data():
    """
    Retrieves chat data from the chat data file.
    """
    if not os.path.exists(CHAT_DATA_PATH):
        return []
    try:
        with open(CHAT_DATA_PATH, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        logger.error(f"An error occurred: {e}")
        return []

def get_openai_chat_instance():
    """
    Retrieves an instance of the OpenAI chat API.
    """
    if "openai_des_instance" not in st.session_state:
        st.session_state["openai_des_instance"] = OpenAI(api_key=OPENAI_API_KEY)
    return st.session_state.openai_des_instance

def get_chat_response_openai(message):
    """
    Retrieves a chat response using the OpenAI chat API.
    """
    try:
        model = "gpt-3.5-turbo"
        client = get_openai_chat_instance()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a assistant."},
                {"role": "user", "content": message},
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

def get_conversation_description(message):
    """
    Retrieves a description of the conversation using the OpenAI chat API.
    """
    if not isinstance(message, str):
        message = json.dumps(message)

    question = DESCRIPTION_QUESTION + message
    return get_chat_response_openai(question)