from src.config.appconfig import env_config
from google.oauth2 import service_account
import json

class GCPAuth:

    def __init__(self):
        self.project_id: str = env_config.gcp_project_id
        self.region: str = env_config.gcp_region
        self.secrets_path: str = env_config.gcp_secrets_path

    def load_credentials(self):

        if env_config.env.lower() in ["dev", "staging", "prod"]:
            return None

        with open(self.secrets_path, "r") as file:
            secrets = json.load(file)
        
        credentials = service_account.Credentials.from_service_account_info(
            secrets,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )

        return credentials

    def refresh_auth(self, credentials):

        "Additional layer for AnthropicVertex"
        
        from google.auth.transport.requests import Request  # type: ignore[import-untyped]
        credentials.refresh(Request())

        return credentials

    def generate_access_token(self, credentials) -> str:

        "Additional layer for AnthropicVertex"
        
        _credentials = self.refresh_auth(credentials)
        access_token = _credentials.token
        # print(access_token)

        if not access_token:
            raise RuntimeError("Could not resolve API token from the environment")

        assert isinstance(access_token, str)
        return access_token
