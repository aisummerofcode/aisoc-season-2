import os, groq, time
from llama_index.llms.groq import Groq
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings, load_index_from_storage
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import tiktoken

from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

models = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
]

llm_client = groq.Groq(api_key=GROQ_API_KEY)

print("Using HuggingFaceEmbedding...")
start_time = time.time()
Settings.embed_model = HuggingFaceEmbedding() # we use the default embedding model
print(f"HuggingFaceEmbedding set in {time.time()-start_time} seconds")

DATA_DIR = "./docs"
EMBEDDING_DIR = "./embeddings"
ENCODING_MODEL = "cl100k_base"

def generate(model, system_prompt, query, temperature=0.1):

    response = llm_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{system_prompt}"
            },
            {
                "role": "user",
                "content": f"{query}"
            }
        ],
        response_format={"type": "text"},
        temperature=temperature
    )

    return response.choices[0].message.content

def generate_embedding(dir):
    print("Uploading files...")
    start_time = time.time()

    docs = SimpleDirectoryReader(input_dir=dir).load_data()
    print(f"Extracting content from {len(docs)} docs...")

    Settings.text_splitter = TokenTextSplitter(chunk_size=1024, chunk_overlap=40)

    index = VectorStoreIndex.from_documents(docs)
    index.storage_context.persist(persist_dir=EMBEDDING_DIR)
    print(f"Vector embedding generated in {time.time()-start_time} seconds!")

    print(f"Computing size of extracted content...")
    content = " ".join([item.text for item in docs])
    num_tokens = tiktoken.get_encoding(ENCODING_MODEL).encode(content)
    print(f"The extracted content has {sum(num_tokens)} tokens")

def retrieve_embedding():
    storage_context = StorageContext.from_defaults(persist_dir=EMBEDDING_DIR)
    return load_index_from_storage(storage_context=storage_context)

def qa_engine(model, index: VectorStoreIndex, query, temperature=0.1):

    llm_rag_client = Groq(model, GROQ_API_KEY, temperature=temperature)
    query_engine = index.as_query_engine(llm_rag_client, similarity_top_k=5)

    return query_engine.query(query)


if __name__=="__main__":

    if len(os.listdir(EMBEDDING_DIR))==0:
        print(f"No embeddings found for data source. Proceeding to generate embedding...")
        generate_embedding(DATA_DIR)

    index = retrieve_embedding()

    query = "What is AI Summer of Code"

    print("\nStarting response generation...\n")
    start_time=time.time()

    response = qa_engine(models[0], index, query)
    print(response)

    print(f"\nResponse generation completed in {time.time()-start_time} seconds")