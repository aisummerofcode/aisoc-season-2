import tempfile, groq, time, traceback
from src.models import *
# from src.prompts import *
from src.config.appconfig import *
from src.application.loghandler import *
from src.application.exceptions import *
from pathlib import Path
from typing import List, Any
from fastapi import FastAPI, Request, UploadFile, Form, Depends
from fastapi.responses import PlainTextResponse, StreamingResponse, JSONResponse
from llama_index.llms.groq import Groq
from llama_index.core.schema import Document
from llama_index.core.node_parser import TokenTextSplitter, SentenceSplitter
from llama_index.core import (
    Settings, 
    SimpleDirectoryReader, 
    # load_index_from_storage, 
    VectorStoreIndex, 
    # StorageContext
)
from llama_index.core.memory.chat_memory_buffer import ChatMemoryBuffer
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from chromadb.config import Settings, DEFAULT_TENANT

API_DIR = Path(__file__).resolve().parent / "../"
LOG_FILENAME = str(API_DIR / "./logs/status_logs.log")
DEFAULT_TEMPERATURE = 0.1

logger = set_logger(
    to_file=True, log_file_name=LOG_FILENAME, to_console=True, custom_formatter=ColorFormmater
)
