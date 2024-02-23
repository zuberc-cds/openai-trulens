# App Setup

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file:

`OPENAI_API_KEY` - The API key for openai service.

`PINECONE_API_KEY` - The API key for pinecone service.


## Installation

Ensure you have the following prerequisites installed:

- Python 3.10 or higher

Then, install the dependencies using pip:

```bash
pip install -r requirements.txt
```

## Running streamlit application

```
streamlit run Helpdesk.py --server.port 8502
```

# Trulens Dashboard Setup

## Installation

Ensure you have the following prerequisites installed:

- Python 3.10 or higher

Then, install the dependencies using pip:

```bash
pip install -r trulens_eval/requirements.txt
```

## Running Trulens Dashboard

```
python trulens_eval/run_trulens_dashboard.py
```