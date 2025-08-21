import os
from dotenv import load_dotenv
load_dotenv()

# load environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
CHROMA_SERVER_HOST = os.getenv("CHROMA_SERVER_HOST", "127.0.0.1")
CHROMA_SERVER_PORT = int(os.getenv("CHROMA_SERVER_HTTP_PORT", "8001"))
CHROMA_SERVER_SSL = os.getenv("CHROMA_SERVER_SSL", "false").lower() in ("1", "true", "yes") # retunrs False if there's no CHROMADB_SSL in .env or if CHROMADB_SSL==""
