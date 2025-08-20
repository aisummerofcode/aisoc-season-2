"""
Alternative FastAPI Backend for RAG Chat Application (Demo Version)

This is an optional reference implementation that demonstrates a different approach
to building the RAG backend. It's NOT used when running your main app.py, but serves
as a comparison and learning tool.

Key Differences from main app.py:
- Uses embedded ChromaDB instead of server mode
- Implements session management in memory
- Provides different endpoint structure (/upload, /chat/start, /chat)
- Uses synchronous responses instead of streaming
- Simpler architecture for educational purposes

Architecture:
Client → FastAPI (this file) → Embedded ChromaDB → LLM (Groq)

Note: Keep this file for comparison with the main streaming implementation
or for future use in different deployment scenarios.
"""

import os
from uuid import uuid4
from typing import List, Optional, Dict

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import chromadb
from chromadb.config import Settings

from llama_index.core import VectorStoreIndex, ServiceContext, StorageContext, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq

# Configuration: Load from environment variables with sensible defaults
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Required: Get from https://console.groq.com/keys
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")  # Local directory for embedded ChromaDB
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_docs")  # ChromaDB collection name

# Allowed LLM models for validation
ALLOWED_MODELS = {"llama3-70b-8192", "mixtral-8x7b-32768"}

# Initialize FastAPI application
app = FastAPI(title="RAG Chat API (Demo)")

# Add CORS middleware to allow cross-origin requests (needed for web frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins (restrict in production)
    allow_credentials=True,     # Allow cookies and auth headers
    allow_methods=["*"],        # Allow all HTTP methods
    allow_headers=["*"]         # Allow all headers
)

# Initialize embedded ChromaDB (different from server mode in main app)
# This creates a local database file instead of connecting to external server
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

# Initialize embedding model for converting text to vectors
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

# Create vector store wrapper around ChromaDB collection
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# In-memory session storage (lost when server restarts)
# In production, you'd use Redis, database, or persistent storage
sessions: Dict[str, Dict] = {}

class ChatStartRequest(BaseModel):
    """
    Request model for starting a new chat session.
    
    This endpoint allows clients to initialize a chat session with
    specific configuration before sending messages.
    """
    chatbot_name: Optional[str] = "Assistant"  # Custom name for the bot
    model: Optional[str] = Field(default="llama3-70b-8192")  # LLM model to use
    temperature: Optional[float] = Field(default=0.2, ge=0.0, le=1.0)  # Response randomness

class ChatRequest(BaseModel):
    """
    Request model for sending chat messages.
    
    Contains the user's query and session information needed
    to maintain conversation context and configuration.
    """
    query: str              # User's question or message
    model: str              # LLM model to use for this request
    chat_uid: str           # Unique session identifier
    chatbot_name: str       # Bot name for personalization
    temperature: Optional[float] = Field(default=0.2, ge=0.0, le=1.0)  # Response creativity

class ChatResponse(BaseModel):
    """
    Response model for chat messages.
    
    Returns the bot's answer along with source information
    for transparency about which documents were used.
    """
    chat_uid: str           # Session identifier for tracking
    answer: str             # Bot's response to the query
    sources: List[dict] = []  # Source documents used for context

def clamp_temp(t: Optional[float]) -> float:
    """
    Ensure temperature value is within valid range [0.0, 1.0].
    
    Temperature controls randomness in LLM responses:
    - 0.0 = deterministic, focused responses
    - 1.0 = creative, varied responses
    
    Args:
        t: Temperature value to validate
        
    Returns:
        float: Clamped temperature between 0.0 and 1.0
    """
    try:
        return max(0.0, min(1.0, float(t if t is not None else 0.2)))
    except Exception:
        return 0.2  # Safe default if conversion fails

def build_chat_engine(model_name: str, temperature: float):
    """
    Create a chat engine with specified model and temperature.
    
    This function initializes the complete RAG pipeline:
    1. Validates and sets up the LLM
    2. Creates service context with embeddings
    3. Builds vector index from stored documents
    4. Returns configured chat engine
    
    Args:
        model_name: Name of the Groq model to use
        temperature: Response randomness setting
        
    Returns:
        Chat engine ready for conversation
    """
    # Validate model name against allowed list
    if model_name not in ALLOWED_MODELS:
        model_name = "llama3-70b-8192"  # Fallback to default
    
    # Ensure temperature is in valid range
    temperature = clamp_temp(temperature)
    
    # Initialize Groq LLM with configuration
    llm = Groq(api_key=GROQ_API_KEY, model=model_name, temperature=temperature)
    
    # Create service context combining LLM and embedding model
    svc = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
    
    # Build vector index from existing documents in ChromaDB
    idx = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=svc)
    
    # Return chat engine with RAG configuration
    return idx.as_chat_engine(
        similarity_top_k=5,        # Retrieve top 5 most relevant chunks
        response_mode="compact",   # Concise response format
        chat_mode="best"          # Use best available chat mode
    )

@app.post("/upload")
async def upload(
    files: List[UploadFile] = File(default=[]),  # Multiple file upload support
    text: Optional[str] = Form(default=None),    # Optional direct text input
    chunk_size: int = Form(default=1000),        # Size of text chunks for processing
    chunk_overlap: int = Form(default=150),      # Overlap between chunks for context
):
    """
    Upload and index documents for RAG retrieval.
    
    This endpoint processes uploaded files and optional text, splits them into
    chunks, generates embeddings, and stores them in ChromaDB for later retrieval.
    
    Process:
    1. Read uploaded files and decode text content
    2. Split documents into overlapping chunks
    3. Generate embeddings for each chunk
    4. Store in ChromaDB vector database
    5. Persist changes to disk
    
    Args:
        files: List of uploaded files (PDF, TXT, etc.)
        text: Optional direct text input
        chunk_size: Maximum tokens per chunk
        chunk_overlap: Tokens to overlap between chunks
        
    Returns:
        dict: Statistics about indexing process
    """
    # Initialize text splitter with specified parameters
    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs: List[Document] = []

    # Process each uploaded file
    for f in files:
        # Read file content as bytes
        data = await f.read()
        
        try:
            # Try UTF-8 decoding first (most common)
            content = data.decode("utf-8", errors="ignore")
        except Exception:
            # Fallback to latin-1 if UTF-8 fails
            content = data.decode("latin-1", errors="ignore")
        
        # Create document with metadata
        docs.append(Document(
            text=content, 
            metadata={"source": f.filename}  # Track source file
        ))

    # Add direct text input if provided
    if text:
        docs.append(Document(
            text=text, 
            metadata={"source": "inline"}  # Mark as direct input
        ))

    # Validate we have documents to process
    if not docs:
        return {
            "indexed_docs": 0, 
            "total_chunks": 0, 
            "warnings": ["No documents provided"]
        }

    # Split documents into chunks for better retrieval
    nodes = []
    for d in docs:
        # Get chunks from each document
        nodes.extend(splitter.get_nodes_from_documents([d]))

    # Add chunks to existing vector index
    idx = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    idx.insert_nodes(nodes)  # Insert new document chunks
    
    # Persist changes to disk (important for embedded ChromaDB)
    chroma_client.persist()

    return {
        "indexed_docs": len(docs),     # Number of documents processed
        "total_chunks": len(nodes),    # Number of chunks created
        "warnings": []                 # Any processing warnings
    }

@app.post("/chat/start")
def chat_start(req: ChatStartRequest):
    """
    Initialize a new chat session with specified configuration.
    
    This endpoint creates a new chat session, builds the chat engine
    with the requested model and settings, and returns session details.
    
    Args:
        req: Chat start request with model, temperature, and bot name
        
    Returns:
        dict: Session details including chat_uid for future requests
    """
    # Generate unique session identifier
    chat_uid = str(uuid4())
    
    # Build chat engine with requested configuration
    engine = build_chat_engine(req.model, req.temperature or 0.2)
    
    # Store session in memory for future requests
    sessions[chat_uid] = {
        "engine": engine,                           # Configured chat engine
        "model": req.model,                        # Model name for tracking
        "temperature": clamp_temp(req.temperature), # Validated temperature
        "chatbot_name": req.chatbot_name,          # Bot name for responses
    }
    
    return {
        "chat_uid": chat_uid,                      # Session ID for client
        "model": req.model,                        # Confirmed model
        "temperature": clamp_temp(req.temperature), # Confirmed temperature
        "chatbot_name": req.chatbot_name,          # Confirmed bot name
    }

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Process a chat message and return response with sources.
    
    This endpoint handles the main chat functionality:
    1. Retrieves or creates chat session
    2. Updates configuration if changed
    3. Processes query through RAG pipeline
    4. Returns response with source information
    
    Args:
        req: Chat request with query and session details
        
    Returns:
        ChatResponse: Bot response with source documents
    """
    # Try to retrieve existing session
    sess = sessions.get(req.chat_uid)
    
    if sess is None:
        # Create new session if not found
        sess = {
            "engine": build_chat_engine(req.model, req.temperature),
            "model": req.model,
            "temperature": clamp_temp(req.temperature),
            "chatbot_name": req.chatbot_name,
        }
        sessions[req.chat_uid] = sess
    else:
        # Update session if model or temperature changed
        if sess["model"] != req.model or sess["temperature"] != clamp_temp(req.temperature):
            # Rebuild chat engine with new settings
            sess["engine"] = build_chat_engine(req.model, req.temperature)
            sess["model"] = req.model
            sess["temperature"] = clamp_temp(req.temperature)
        
        # Always update bot name (can change per request)
        sess["chatbot_name"] = req.chatbot_name

    # Process query through RAG chat engine
    resp = sess["engine"].chat(req.query)

    # Extract source information for transparency
    sources: List[dict] = []
    for s in getattr(resp, "source_nodes", []) or []:
        try:
            sources.append({
                "score": float(s.score) if s.score is not None else None,  # Relevance score
                "snippet": s.node.get_content()[:300],  # First 300 chars of source
                "source": s.node.metadata.get("source"),  # Source file name
            })
        except Exception:
            # Skip sources that can't be processed
            pass

    return ChatResponse(
        chat_uid=req.chat_uid,  # Echo back session ID
        answer=str(resp),       # Bot's response
        sources=sources         # Source documents used
    )

"""
Key Learning Points for Students:

1. EMBEDDED vs SERVER CHROMADB:
   - This demo uses embedded ChromaDB (local file storage)
   - Main app.py uses server mode (separate process)
   - Embedded: simpler setup, single application
   - Server: better for production, multiple applications

2. SESSION MANAGEMENT:
   - In-memory sessions (lost on restart)
   - Production would use Redis or database
   - Each session maintains its own chat engine

3. SYNCHRONOUS vs STREAMING:
   - This demo returns complete responses
   - Main app streams tokens in real-time
   - Streaming provides better user experience

4. ENDPOINT DESIGN:
   - /upload: Index documents
   - /chat/start: Initialize session
   - /chat: Send messages
   - Different from main app's /index and /chat

5. ERROR HANDLING:
   - Temperature clamping for safety
   - Model validation against allowed list
   - Graceful fallbacks for encoding issues

6. TRANSPARENCY:
   - Returns source information with responses
   - Shows which documents were used
   - Includes relevance scores for debugging
"""