# Load .env file using:
from dotenv import load_dotenv
load_dotenv(override=True)
import os

class EnvConfig:
    """Class to hold environment configuration variables."""
    
    def __init__(self):
        self.environment = os.getenv("PYTHON_ENV")
        self.app_port = os.getenv("PORT")
        self.x_api_key = os.getenv("X_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.database = os.getenv("DB_DATABASE")
        self.mongo_conn_url = os.getenv("DB_CONN_URL")
        self.mongo_database_name = os.getenv("DB_DBNAME")

        

        
    def __repr__(self):
        return (
            f"EnvConfig(env={self.env}, app_port={self.app_port}, "
            f"database={self.database}, user={self.user}, password=****)"
        )

# Create an instance of EnvConfig to access the environment variables
env_config = EnvConfig()