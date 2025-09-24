import groq
from llama_index.llms.groq import Groq
from typing import Literal
from src.config import (
    GROQ_API_KEY
)

# models via groq
GPT_OSS_20B = "openai/gpt-oss-20b"                              # 8k token context window
GPT_OSS_120B = "openai/gpt-oss-120b"                            # 8k
LLAMA_3_1_8B = "llama-3.1-8b-instant"                           # 6k
LLAMA_3_3_70B = "llama-3.3-70b-versatile"                       # 12k
LLAMA_4_SCOUT_17B = "meta-llama/llama-4-scout-17b-16e-instruct" # 30k
KIMI_K2 = "moonshotai/kimi-k2-instruct"                         # 10k
QWEN_3_32B = "qwen/qwen3-32b"                                   # 6k
DEFAULT_EMBED_MODEL = "BAAI/bge-small-en" 


# TODO: add more clients - Vertex, ANthropic, etc
#       add a method to map model names to these clients

class LLMClient:

    task: Literal["base", "rag"] = "rag"

    def get_groq(self):
        return groq.Groq(api_key=GROQ_API_KEY)

    def get_groq_from_llama_index(self, model:str):
        return Groq(model, GROQ_API_KEY)
    
    def map_task_to_client(self, task:str, model:str):
        
        task_map = {
            "base": self.get_groq,
            "rag": self.get_groq_from_llama_index
        }

        client = task_map.get(task)

        return client(model)
    
