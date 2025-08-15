from dotenv import load_dotenv
load_dotenv(override=True)
import os




class EnvConfig:
    """This class holds and manages the environment configuration for all env variables"""
    def __init__(self):
        self.env = os.getenv("ENVIRONMENT")
        self.port = os.getenv("PORT")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")


# Create an instance of ENvConfig to be able to access all environment variable
env_config = EnvConfig()