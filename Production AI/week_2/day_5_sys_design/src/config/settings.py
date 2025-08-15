from pydantic_settings import BaseSettings
from src.config.appconfig import env_config




class Setting(BaseSettings):
    """
    This class extands the BaseSetiingts class from pydantic.
    It contains the project definitions.
    """
    
    VERION: str = "v0.0.1"