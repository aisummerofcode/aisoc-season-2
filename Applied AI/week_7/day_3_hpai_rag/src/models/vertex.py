import vertexai, json
from vertexai.generative_models import GenerativeModel
from llama_index.llms.vertex import Vertex
from src.infra.auth import GCPAuth


class VertexClient(GCPAuth):

    def base_model(self, model: str):
        vertexai.init(
            project=self.project_id, 
            location=self.region
        )
        return GenerativeModel(model)

    def rag_model(self, model: str, temperature=0.1, max_tokens=1024, context_window=128000):
        credentials = self.load_credentials()
        model = Vertex(
            model=model,
            project=self.project_id,
            location=self.region,
            credentials=credentials,
            temperature=temperature,
            context_window=context_window,
            max_tokens=max_tokens
        )
        
