import os
import time
import openai
import requests
from dotenv import load_dotenv
from llama_index.core import Settings
import llama_index.core
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.pinecone import PineconeVectorStore
from logger import AppLogger
from pinecone import Pinecone
from utils import get_logger
from constant import *

load_dotenv()

logging = get_logger()

class OpenAIChat:
    def __init__(self):
        self.setup_openai_api()
        self.setup_pinecone()
        self.setup_llama_index_settings()
        self.setup_chat_engine()

    def setup_openai_api(self):
        """
        Set up the OpenAI API by setting the API key from the environment variable and configuring the OpenAI API with the key.
        """
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
        logging.info("OpenAI API has been set up.")

    def setup_pinecone(self):
        """
        Sets up the pinecone by retrieving the API key from the environment variables and creating a pinecone index.
        """
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index = self.create_pinecone_index(pinecone_api_key)
        logging.info("Pinecone has been set up.")

    def create_pinecone_index(self, pinecone_api_key):
        """
        Create a Pinecone index using the provided Pinecone API key.

        Args:
            pinecone_api_key (str): The API key for accessing the Pinecone service.

        Returns:
            Pinecone Index: The created Pinecone index for the specified collection.
        """
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index("chatbot1")
        logging.info("Pinecone index has been created.")
        return index
    
    def setup_llama_index_settings(self):
        """
        Set up the llama index settings including creating an OpenAI model, setting various settings, and logging the result.
        """
        llm = OpenAI(model="gpt-3.5-turbo-0125", temperature=0)
        Settings.llm = llm
        Settings.embed_model = OpenAIEmbedding(embed_batch_size=50)
        Settings.text_splitter = SentenceSplitter()
        Settings.transformations = [SentenceSplitter(chunk_size=1024)]
        logging.info("Llama index settings have been set up.")

    def setup_chat_engine(self):
        """
        Initializes the chat engine by loading documents, vector store, and creating chat engine. 
        Then, it reindexes the documents.
        """
        self.documents = self.load_documents()
        self.base_index = self.load_vector_store()
        self.chat_engine_base = self.create_chat_engine()
        self.reindex_documents()
        logging.info("Chat engine has been initialized and documents have been reindexed.")
        
    def reindex_documents(self):
        """
        Reindexes documents if requested, and logs the status of the reindexing process.
        """
        # reindex_requested = os.getenv("REINDEX", "no").lower() == "yes"
        if REINDEX:
            self.base_index = self.index_documents()
            logging.info("Documents have been reindexed as requested.")
        else:
            logging.info("Reindexing not requested. Using the existing index.")
            
    def initialize_pinecone_vector_store(self):
        """
        Initializes the pinecone vector store using the provided pinecone index and returns a PineconeVectorStore object.
        """
        store = PineconeVectorStore(pinecone_index=self.pinecone_index)
        logging.info("Pinecone vector store has been initialized.")
        return store
    
    def index_documents(self):
        """
        Indexes documents and returns the base index.

        Returns:
            VectorStoreIndex: The base index of the indexed documents.
        """
        vector_store = self.initialize_pinecone_vector_store()
        base_node_parser = SentenceSplitter()
        base_nodes = base_node_parser.get_nodes_from_documents(self.documents)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        base_index = VectorStoreIndex(base_nodes, storage_context=storage_context)
        logging.info("Documents have been indexed and saved.")
        return base_index
    
    def load_documents(self):
        """
        Load documents from a simple directory reader and log the number of documents loaded. 

        :return: The loaded documents.
        """
        documents = SimpleDirectoryReader(SOP_DATA_PATH).load_data()
        logging.info(f"Loaded {len(documents)} documents.")
        return documents
    
    def load_vector_store(self):
        """
        Load the vector store and create a vector store index from it.

        :return: Vector store index
        """
        vector_store = PineconeVectorStore(pinecone_index=self.pinecone_index)
        index = VectorStoreIndex.from_vector_store(vector_store)
        logging.info("Vector store has been loaded and index has been created.")
        return index

    def create_chat_engine(self):
        """
        Create a chat engine using the system prompt and return it.
        """
        system_prompt = self.get_system_prompt()
        chat_engine = self.base_index.as_chat_engine(
            chat_mode="context",
            streaming=True,
            memory=ChatMemoryBuffer.from_defaults(token_limit=3000),
            system_prompt=system_prompt,
        )
        logging.info("Chat engine has been created.")
        return chat_engine

    def get_system_prompt(self):
        """
        Get the system prompt for Crest Data Systems' assistant.
        """
        return (
            "As Crest Data Systems' assistant, provide precise, complete answers and engage smoothly."
            "Note that you should answer user queries based on the documents you have indexed. Ensure to give your answer in well-defined steps."
            "Ensure to answer all the questions with respect to crest data systems."
            "If you don't know the correct answer, prepend the following at the start of the response: Although I couldn't find anything in our knowledge base, here are the general steps to follow. and append the following at the end of the answer: Please contact Crest IT support at IT Helpdesk google chat for further assistance."
        ) 

    def reset_chat_engine(self):
        """
        Reset the chat engine.
        """
        self.chat_engine_base.reset()

    # Function to interact with the chat engine
    def ask_and_respond(self, user_query):
        """
        Function to ask a user query and get a response from the chat engine.
        
        :param user_query: the query entered by the user
        :return: the response stream from the chat engine
        """
        start_time = time.time()
        response_stream = self.chat_engine_base.stream_chat(user_query)
        end_time = time.time()
        logging.info(f"Time taken for this response: {end_time - start_time}")
        return response_stream

    def extract_response_data(self, response):
        """Extracts the response data from the API response."""
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return "API request failed with status code: " + str(response.status_code)

    def start_image_processing(self, image_base64, user_query=DEFAULT_USER_QUERY, image_type="image/png"):
        """Processes an image given in base64 encoding and a user query to generate a response using OpenAI's Vision API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.openai_api_key,
        }
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {

                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What is the overall issue that user is facing in this image? Start with I am facing an issue.... Pay special attention to the software name and any errors contained in the screenshot. Give a detailed 1 liner answer.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_type};base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 300,
        }

        response = requests.post(url, headers=headers, json=payload)
        content = self.extract_response_data(response)
        user_query = user_query + " " + content
        logging.info("User query after image processing: " + user_query)
        response = self.ask_and_respond(user_query)
        return response