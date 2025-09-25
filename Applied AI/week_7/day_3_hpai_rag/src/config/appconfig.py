import os

from dotenv import load_dotenv
load_dotenv(override=True)

class EnvConfig:
    """Class to hold environment configuration variables."""
    
    def __init__(self):
        self.env = os.getenv("ENV")
        self.gcp_project_id = os.getenv("GCP_PROJECT_ID")
        self.gcp_region = os.getenv("GCP_REGION")
        self.app_port = os.getenv("PORT")
        self.database = os.getenv("VECTOR_DB")
        self.chroma_server_host = os.getenv("CHROMA_SERVER_HOST")
        self.chroma_server_port = os.getenv("CHROMA_SERVER_HTTP_PORT")
        self.chroma_use_server = os.getenv("CHROMA_USE_SERVER", "false").lower() in ("1", "true", "yes")
        self.chroma_server_ssl = self.chroma_use_server
        self.chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR")
        self.data_dir = os.getenv("DATA_DIR")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

    def __repr__(self):
        return (
            f"EnvConfig(env={self.env}, app_port={self.app_port}, "
            f"database={self.database}, chroma_={self.chroma_server_host})"
        )

# Create an instance of EnvConfig to access the environment variables
env_config = EnvConfig()