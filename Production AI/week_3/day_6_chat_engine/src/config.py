import os
from dotenv import load_dotenv
load_dotenv()

# load environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
CHROMADB_HOST = os.environ.get("CHROMADB_HOST")
CHROMADB_PORT = os.environ.get("CHROMADB_PORT")
CHROMADB_SSL = bool(os.environ.get("CHROMADB_SSL")) # retunrs False if there's no CHROMADB_SSL in .env or if CHROMADB_SSL==""