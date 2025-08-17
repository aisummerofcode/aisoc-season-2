import tempfile, groq, time, traceback
from src.config import *
from src.loghandler import *
from src.exceptions import *
from pathlib import Path
from typing import List, Any
from fastapi import FastAPI, Request, UploadFile, Form, Depends
from fastapi.responses import PlainTextResponse, StreamingResponse, JSONResponse
from llama_index.llms.groq import Groq
from llama_index.core.schema import Document
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import tiktoken, chromadb


API_DIR = Path(__file__).resolve().parent / "../"
LOG_FILENAME = str(API_DIR / "./logs/status_logs.log")
DEFAULT_EMBED_MODEL = "BAAI/bge-small-en"


logger = set_logger(
    to_file=True, log_file_name=LOG_FILENAME, to_console=True, custom_formatter=ColorFormmater
)

ALLOWED_FILES = [
    "txt", "csv", "htm", "html", "pdf", "json", "doc", "docx", "pptx"
]


def is_allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".",1)[-1].lower() in ALLOWED_FILES

def run_file_checks(files: List[UploadFile]):

    if not files:
        message = f"No file found"
        logger.error(message)
        return JSONResponse(
            content={
                "status": message},
            status_code=400
        )
    
    for file in files:
        filename = file.filename
        if not file or filename == "":
            message = f"No selected file"
            logger.error(message)
            return JSONResponse(
                content ={
                    "status": message
                },
                status_code=400
            )
        
        if not is_allowed_file(filename):
            message = f"File format {filename.rsplit('.',1)[-1].lower()} not supported. Use any of {ALLOWED_FILES}"
            logger.warning(message)
            return JSONResponse(
                content={"status": message},
                status_code=415
            )
    
    return JSONResponse(
        content={        
            "status": "success"
        },
        status_code=200
    )

async def upload_files(
    files: List[UploadFile], 
    temp_dir: tempfile.TemporaryDirectory
):
    file_checks = run_file_checks(files)
    if file_checks.status_code==200:
        filename = ""
        try:
            for file in files:
                filename = file.filename
                filepath = os.path.join(temp_dir, filename)
                file_obj = await file.read()

                with open(filepath, "wb") as buffer:
                    buffer.write(file_obj)
    
    
            message = f"Files uploaded successfully."
            logger.info(message)
            return JSONResponse(
                content={"status": message},
                status_code=200
            )
        
        except Exception as e:
            message = f"An error occured while trying to upload the file, {filename}: {e}"
            logging.error(message)
            raise UploadError(message)
        
    raise FileCheckError(file_checks["status"])

def init_chroma(collection_name):
    logger.info(f"Initializing Chroma database...")
    try:
        print(F"CHROMADB_SSL >> {CHROMADB_SSL}")
        chroma_client = chromadb.HttpClient(
            host=CHROMADB_HOST,
            port=CHROMADB_PORT,
            ssl=True
        ) if CHROMADB_SSL \
            else chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        
    except Exception as e:
        message = f"Error connecting to Chroma database for collection `{collection_name}`: {e}"
        logger.error(message)
        raise ChromaConnectionError(message)

    collection = chroma_client.get_or_create_collection(
        collection_name,
        embedding_function=None,
        metadata={"hnsw": "cosine"}
    )
    logger.info(f"Collection created or retrieved: {collection_name}")
    return collection

async def generate_and_store_embeddings(chat_uid, documents: List[Document], embed_model:str=DEFAULT_EMBED_MODEL):
    
    collection_name = f"aisoc-{chat_uid}-embeddings"

    try:
        logger.info(f"Generating vector embeddings for collection: {collection_name}...")
        start_time = time.time()
        embed_func = HuggingFaceEmbedding(
            model_name=embed_model,
            # device="cuda"
        )

        docs = [doc.text for doc in documents]
        metadata_list = [doc.metadata for doc in documents]
        id_list = [f"embedding-{i+1}" for i in range(len(documents))]
        embeddings = [embed_func.get_text_embedding(doc.text) for doc in documents]
        logger.info(f"Embeddings generated for collection: {collection_name} in {time.time()-start_time} seconds.")
    
    except Exception as e:
        message = f"Error generating embeddings for collection: {collection_name}"
        logger.error(message)
        raise EmbeddingError(message)
        
    # populate chroma collection with embeddings
    chroma_collection = init_chroma(collection_name)
    logger.info(f"Populating collection {collection_name} with computed embeddings...")
    chroma_collection.upsert(
        ids=id_list,
        documents=docs,
        metadatas=metadata_list,
        embeddings=embeddings
    )

    # inspect collection
    if chroma_collection.count() == 0:
        message = f"Could not store embeddings in Chroma database. Collection is empty!"
        logger.error(message)
        raise ChromaCollectionError(message)




