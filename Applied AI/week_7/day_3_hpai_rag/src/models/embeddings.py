from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.vertex import VertexTextEmbedding
from src.infra.auth import GCPAuth

class EmbedModel(GCPAuth):

    DEFAULT_EMBED_MODEL = "BAAI/bge-small-en" 

    def vertex(self, model):
        credentials = self.load_credentials()
        return VertexTextEmbedding(
            model_name=model,
            project=self.project_id,
            location=self.region,
            credentials=credentials,
        )

    def huggingface(self, model=None):
        return HuggingFaceEmbedding(
            model=model or self.DEFAULT_EMBED_MODEL
        )