from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    """
    This class extends the BaseSettings class from FastAPI.
    It contains the project definitions.

    Args:
        None.

    Returns:
        class: extends the settings class.
    """

    API_STR: str = "/api/v1"
    VERSION: str = "3.0.2"
    PROJECT_NAME: str = "Agentic AI Server"



def get_setting():
    """
    Return the settings object.

    Args:
        None.

    Returns:
        class: extends the settings class.
    """
    return Settings()
