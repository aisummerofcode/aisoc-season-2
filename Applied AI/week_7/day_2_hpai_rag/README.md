# AISOC Chat Engine v1

This project is a RAG-powered chatbot application built with FastAPI, LlamaIndex, and ChromaDB. It allows users to upload documents, which are then used to create a knowledge base for a chatbot to answer questions.

## Features

*   **File Upload**: Supports uploading various file types (txt, pdf, docx, etc.) to build a knowledge base.
*   **Vector Embeddings**: Generates and stores vector embeddings for the uploaded documents using HuggingFace models.
*   **ChromaDB Integration**: Uses ChromaDB as a vector store for efficient similarity search.
*   **Chat API**: Provides a chat endpoint to interact with the RAG-powered chatbot.
*   **LLM Integration**: Integrates with LLMs via Groq for response generation.
*   **GCS Integration**: Includes scripts for mounting a Google Cloud Storage bucket to persist data.

## Architecture Overview

The application consists of the following components:

1.  **FastAPI Backend**: A Python web server that exposes API endpoints for file upload and chat.
2.  **LlamaIndex**: The core RAG framework used for data indexing, embedding, and querying.
3.  **ChromaDB**: The vector database used to store and retrieve document embeddings.
4.  **Groq**: The LLM inference service used to generate responses.
5.  **Google Cloud Storage (GCS)**: Used for persistent storage of the ChromaDB database.

The workflow is as follows:
1.  A user uploads documents via the `/index` endpoint.
2.  The application processes the documents, generates vector embeddings, and stores them in a ChromaDB collection.
3.  The ChromaDB database is persisted in a GCS bucket.
4.  A user sends a query to the `/chat` endpoint.
5.  The application retrieves relevant documents from ChromaDB based on the query.
6.  The retrieved documents and the user's query are passed to a large language model (LLM) via Groq.
7.  The LLM generates a response, which is streamed back to the user.

## Prerequisites

*   A Google Cloud Platform (GCP) project.
*   A GCP VM instance (Debian-based Linux is recommended).
*   Google Cloud SDK installed on your local machine.
*   A Google Cloud Storage bucket.
*   Python 3.8+

## Setup and Installation

These steps should be performed on your GCP VM instance.

1.  **SSH into your GCP VM:**

    ```bash
    gcloud compute ssh <your-vm-instance-name> --zone <your-zone>
    ```

2.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

3.  **Install Python dependencies:**

    ```bash
    sudo apt-get update
    sudo apt-get install python3-pip
    pip3 install -r requirements.txt
    ```

4.  **Set up Google Cloud Storage Mount:**

    *   Install GCSFuse by following the instructions in the `mount-cmds.sh` script. This will allow you to mount your GCS bucket as a local directory on your VM.
    *   Create a GCS bucket in your GCP project.
    *   Mount the GCS bucket to a directory on your VM (e.g., `/mnt/storage`). The `mount-cmds.sh` script provides the necessary commands. This mounted directory will be used to persist the ChromaDB data.

5.  **Configure environment variables:**

    Create a `.env` file in the root of the project and add the following variables:

    ```
    GROQ_API_KEY="your-groq-api-key"
    CHROMADB_HOST="localhost"
    CHROMADB_PORT="8000"
    CHROMA_USE_SERVER="true" # or "false" to use a persistent client
    CHROMA_PATH="/mnt/storage/chroma_db" # Path within the GCS mount
    ```

## Deployment

1.  **Start the FastAPI server:**

    It's recommended to run the application using a process manager like `gunicorn` or `systemd` for production.

    For development and testing, you can use `uvicorn`:
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 5000 --reload
    ```
    Make sure your VM's firewall rules allow traffic on port 5000.

2.  **Create a knowledge base:**

    Send a POST request to the `/index` endpoint with the files you want to process.

    ```bash
    curl -X POST -F "chat_uid=my-chat" -F "files=@/path/to/your/file.txt" http://<your-vm-external-ip>:5000/index
    ```

3.  **Chat with the application:**

    Send a POST request to the `/chat` endpoint with your query.

    ```json
    {
      "query": "What is the main topic of the document?",
      "model": "llama-3.1-8b-instant",
      "chat_uid": "my-chat",
      "chatbot_name": "MyChatbot"
    }
    ```

    Example using `curl`:

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{
      "query": "What is the main topic of the document?",
      "model": "llama-3.1-8b-instant",
      "chat_uid": "my-chat",
      "chatbot_name": "MyChatbot"
    }' http://<your-vm-external-ip>:5000/chat
    ```

## API Endpoints

*   `GET /health`: Health check endpoint.
*   `POST /index`: Upload files to create a knowledge base.
*   `POST /chat`: Send a query to the chatbot.

## Project Structure

```
.
├── app.py              # FastAPI application
├── mount-cmds.sh       # GCS mount commands
├── requirements.txt    # Python dependencies
└── src
    ├── config.py       # Configuration and environment variables
    ├── exceptions.py   # Custom exceptions
    ├── helpers.py      # Core application logic
    ├── loghandler.py   # Logging setup
    ├── models.py       # LLM models
    └── prompts.py      # Chatbot prompts
```
