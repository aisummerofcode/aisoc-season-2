import tempfile, groq, time, traceback
from src.models import *
from src.prompts import *
from src.config import *
from src.loghandler import *
from src.exceptions import *
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


API_DIR = Path(__file__).resolve().parent / "../"
LOG_FILENAME = str(API_DIR / "./logs/status_logs.log")
DEFAULT_TEMPERATURE = 0.1

logger = set_logger(
    to_file=True, log_file_name=LOG_FILENAME, to_console=True, custom_formatter=ColorFormmater
)

class TempAppState:
    chat_memory: ChatMemoryBuffer

class FileUtils:

    ALLOWED_FILES: List = [
        "txt", "csv", "htm", "html", "pdf", "json", "doc", "docx", "pptx"
    ]

    def is_allowed_file(self, filename:str) -> bool:
        return "." in filename and filename.rsplit(".",1)[-1].lower() in self.ALLOWED_FILES

    def run_file_checks(self, files: List[UploadFile]):

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
            
            if not self.is_allowed_file(filename):
                message = f"File format {filename.rsplit('.',1)[-1].lower()} not supported. Use any of {self.ALLOWED_FILES}"
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
        self,
        files: List[UploadFile], 
        temp_dir: tempfile.TemporaryDirectory
    ):
        file_checks = self.run_file_checks(files)
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

class EmbeddingUtils:

    tokenizer = SentenceSplitter()._tokenizer
    text_splitter = SentenceSplitter()._split_text

    embed_model: str = DEFAULT_EMBED_MODEL
    embed_func = HuggingFaceEmbedding(
        model_name=embed_model,
    )

    async def generate_and_store_embeddings(
        self,
        chat_uid: str,
        documents: List[Document]
    ):

        collection_name = f"aisoc-{chat_uid}-embeddings"
        chroma_collection = ChromaUtils().init_chroma(collection_name, task="create")

        try:
            logger.info(f"Generating vector embeddings for collection: {collection_name}...")
            start_time = time.time()

            doc_split_by_chunk_size = [
                (
                    [
                        {"content": item, "metadata": doc.metadata}
                        for item in self.text_splitter(doc.text, chunk_size=1024)
                    ]
                    if len(self.tokenizer(doc.text)) > 1536
                    else [{"content": doc.text, "metadata": doc.metadata}]
                )
                for doc in documents
            ]  # nested list

            doc_chunks = sum(doc_split_by_chunk_size, []) # flatten nested list
            content_list = [doc["content"] for doc in doc_chunks]
            metadata_list = [doc["metadata"] for doc in doc_chunks]

            id_list = [f"embedding-{i+1}" for i in range(len(content_list))]

            embeddings = [self.embed_func.get_text_embedding(item) for item in content_list]
            # logger.info(f"Document token sizes: {[len(self.tokenizer(item)) for item in content_list]}")
            logger.info(f"Embeddings generated for collection: {collection_name} in {time.time()-start_time} seconds.")

        except Exception as e:
            message = f"Error generating embeddings for collection: {collection_name}. Error: {e}"
            logger.error(message)
            raise EmbeddingError(message)

        # populate chroma collection with embeddings
        logger.info(f"Populating collection {collection_name} with computed embeddings...")
        chroma_collection.upsert(
            ids=id_list,
            documents=content_list,
            metadatas=metadata_list,
            embeddings=embeddings
        )

        # inspect collection
        collection_count = chroma_collection.count()
        if collection_count == 0:
            message = f"Could not store embeddings in Chroma database. Collection is empty!"
            logger.error(message)
            raise ChromaCollectionError(message)

        logger.info(f"Collection size::{collection_count}")

    async def retrieve_embeddings(self, chat_uid: str):

        collection_name = f"aisoc-{chat_uid}-embeddings"
        chroma_collection = ChromaUtils().init_chroma(collection_name)

        collection_count = chroma_collection.count()
        if collection_count == 0:
            message = f"Could not find embeddings in ChromaDB for conversation {chat_uid}. Please pass the correct chat_uid."
            logger.error(message)
            raise ChromaCollectionError(message)

        chroma_vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        embeddings = VectorStoreIndex.from_vector_store(
            vector_store=chroma_vector_store,
            embed_model=self.embed_func
        )
        logger.info(f"Embeddings retrieved from ChromaDB for collection {collection_name}")

        return embeddings, collection_count

class ChromaUtils:

    def get_chroma_client(self, use_server: bool = True):
        if use_server:
            # Only use server mode if explicitly requested
            if CHROMA_SERVER_SSL:
                chroma_client = chromadb.HttpClient(
                    host=CHROMA_SERVER_HOST, port=CHROMA_SERVER_PORT, ssl=True
                )
            else:
                chroma_client = chromadb.HttpClient(
                    host=CHROMA_SERVER_HOST, port=CHROMA_SERVER_PORT
                )
        else:
            # Embedded, on-disk Chroma (recommended for local dev)
            chroma_path = os.getenv("CHROMA_PATH", "./chroma_db")
            # For recent Chroma, 'path' is the kw. Older versions may use 'persist_directory'.
            try:
                chroma_client = chromadb.PersistentClient(path=chroma_path)
            except TypeError:
                chroma_client = chromadb.PersistentClient(persist_directory=chroma_path)

        return chroma_client

    def init_chroma(self, collection_name: str, task: str = "retrieve"):
        """
        Initialize Chroma in embedded mode by default (no external server).
        If you really need to use an external server, set CHROMA_USE_SERVER=true and provide CHROMA_SERVER_HOST/PORT.
        """
        use_server = os.getenv("CHROMA_USE_SERVER", "false").lower() in ("1", "true", "yes")
        logger.info(f"Initializing Chroma database...")

        try:
            chroma_client = self.get_chroma_client(use_server=use_server)

        except Exception as e:
            message = f"Error connecting to Chroma database for collection `{collection_name}`: {e}"
            logger.error(message)
            raise ChromaConnectionError(message)

        collection = chroma_client.get_or_create_collection(
            collection_name,
            embedding_function=None, # we are not passing an embedding_func here as we are handling embedding generation in generate_and_store_embeddings()
            metadata={"hnsw": "cosine"}
        )
        logger.info(f"Collection {task}d: {collection_name}")
        return collection

class ChatEngine:

    async def generate_response(
        self,
        query: str,
        chat_uid: str,
        model: str = LLAMA_3_3_70B,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        chatbot_name: str = "",
        chat_mode: str = "context",
        verbose: bool = True,
        streaming: bool = True,
        app_state: TempAppState = None
    ):
        chatbot_desc = f"Your name is {chatbot_name}. " if chatbot_name else ""
        system_prompt = system_prompt.format(chatbot_desc=chatbot_desc)
        logger.info(f"System prompt::{system_prompt}")

        index, index_size = await EmbeddingUtils().retrieve_embeddings(chat_uid)
        Settings.llm = LLMClient().map_task_to_client(task="rag", model=model)
        # Settings.embed_model = HuggingFaceEmbedding()

        # heuristic for choice_k; experiment until you achieve optimal rule
        # don't use groq models for longer contexts due to rate limit on free plan
        choice_k = 3 if index_size < 20 \
            else 5 if index_size < 50 \
                else index_size//10 if index_size < 200 \
                    else 30
        
        app_state.chat_memory = self.retrieve_chat_memory(choice_k=choice_k, app_state=app_state)

        chat_engine = index.as_chat_engine(
            # llm=llm_client,
            chat_mode=chat_mode,
            system_prompt=system_prompt,
            similarity_top_k=choice_k,
            verbose=verbose,
            streaming=streaming,
            memory=app_state.chat_memory
        )

        response = chat_engine.stream_chat(query)
        logger.info("Starting response stream...\n")
        try:
            for token in response.response_gen:
                print(token, end="")
                yield str(token)
        except:
            message = f"An error occured while generating chat response."
            exception = traceback.format_exc()
            logger.error(f"{message}: {exception}")
            raise ChatEngineError(f"{message}. See the system logs for more information.")

    # Methods for managing chat history within an API session - not ideal for production
    def init_chat_memory(self, choice_k: int):
        token_limit = choice_k*1024
        return ChatMemoryBuffer.from_defaults(token_limit=token_limit)

    def retrieve_chat_memory(self, choice_k:int, app_state:TempAppState=None):
        try:
            logger.info("Retrieving chat memory...")
            return app_state.chat_memory or self.init_chat_memory(choice_k)
        except:
            logger.warning("Could not retrieve chat memory. Creating new memory...")
            return self.init_chat_memory(choice_k)
