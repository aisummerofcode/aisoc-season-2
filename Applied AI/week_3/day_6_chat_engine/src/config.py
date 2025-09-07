import os
from dotenv import load_dotenv
load_dotenv()

# load environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
CHROMADB_HOST = os.environ.get("CHROMADB_HOST")
CHROMADB_PORT = int(os.environ.get("CHROMADB_PORT", "8001"))
CHROMADB_SSL = os.environ.get("CHROMADB_SSL", "false").lower() in ("1", "true", "yes") # returns False if there's no CHROMADB_SSL in .env or if CHROMADB_SSL==""
CHROMA_USE_SERVER = os.environ.get("CHROMA_USE_SERVER", "false").lower() in ("1", "true", "yes")