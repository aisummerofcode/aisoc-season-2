from src.utils.constants import *


class EmbeddingHandler:

    tokenizer = SentenceSplitter()._tokenizer
    text_splitter = SentenceSplitter()._split_text

    embed_model: str = EmbedModel().DEFAULT_EMBED_MODEL
    # embed_func = HuggingFaceEmbedding(
    #     model_name=embed_model,
    # )

    embed_func: str = EmbedModel().huggingface(model=embed_model)

    async def generate_and_store_embeddings(
        self,
        chat_uid: str,
        tenant_id:str,
        documents: List[Document]
    ):

        collection_name = f"aisoc-{chat_uid}-embeddings"
        chroma_collection = ChromaUtils().init_chroma(collection_name, tenant=tenant_id, task="create")

        try:
            logger.info(f"Generating vector embeddings for collection: {collection_name}...")
            start_time = time.time()

            doc_split_by_chunk_size = [
                (
                    [
                        {"content": item, "metadata": doc.metadata}
                        for item in self.text_splitter(doc.text, chunk_size=1024)
                    ]
                    if len(self.tokenizer(doc.text)) > 1536
                    else [{"content": doc.text, "metadata": doc.metadata}]
                )
                for doc in documents
            ]  # nested list

            doc_chunks = sum(doc_split_by_chunk_size, []) # flatten nested list
            content_list = [doc["content"] for doc in doc_chunks]
            metadata_list = [doc["metadata"] for doc in doc_chunks]

            id_list = [f"embedding-{i+1}" for i in range(len(content_list))]

            embeddings = [self.embed_func.get_text_embedding(item) for item in content_list]
            # logger.info(f"Document token sizes: {[len(self.tokenizer(item)) for item in content_list]}")
            logger.info(f"Embeddings generated for collection: {collection_name} in {time.time()-start_time} seconds.")

        except Exception as e:
            message = f"Error generating embeddings for collection: {collection_name}. Error: {e}"
            logger.error(message)
            raise EmbeddingError(message)

        # populate chroma collection with embeddings
        logger.info(f"Populating collection {collection_name} with computed embeddings...")
        chroma_collection.upsert(
            ids=id_list,
            documents=content_list,
            metadatas=metadata_list,
            embeddings=embeddings
        )

        # inspect collection
        collection_count = chroma_collection.count()
        if collection_count == 0:
            message = f"Could not store embeddings in Chroma database. Collection is empty!"
            logger.error(message)
            raise ChromaCollectionError(message)

        logger.info(f"Collection size::{collection_count}")

    async def retrieve_embeddings(self, chat_uid: str):

        collection_name = f"aisoc-{chat_uid}-embeddings"
        chroma_collection = ChromaUtils().init_chroma(collection_name)

        collection_count = chroma_collection.count()
        if collection_count == 0:
            message = f"Could not find embeddings in ChromaDB for conversation {chat_uid}. Please pass the correct chat_uid."
            logger.error(message)
            raise ChromaCollectionError(message)

        chroma_vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        embeddings = VectorStoreIndex.from_vector_store(
            vector_store=chroma_vector_store,
            embed_model=self.embed_func
        )
        logger.info(f"Embeddings retrieved from ChromaDB for collection {collection_name}")

        return embeddings, collection_count

class ChromaUtils:

    def create_new_db(self, db_name: str, tenant=None):
        settings = Settings()
        settings.chroma_api_impl = "chromadb.api.fastapi.FastAPI"
        admin_client = chromadb.AdminClient(settings)
        admin_client.create_database(db_name, tenant or "DEFAULT_TENANT")
        logger.info(f"Database '{db_name}' created in tenant '{tenant}' successfully.")

    def create_new_tenant(
        self,
        # client: chromadb.ClientAPI,
        tenant,
        # tenant: str,
        create_db=True,
        db_name: str = None,
    ):
        settings = Settings()
        settings.chroma_api_impl = "chromadb.api.fastapi.FastAPI"

        # client = chromadb.HttpClient(
        #     host=env_config.chroma_server_host, 
        #     port=env_config.chroma_server_port, 
        #     ssl=env_config.chroma_server_ssl,
        #     settings=settings
        # )
        admin_client = chromadb.AdminClient(settings)
        admin_client.create_tenant(tenant)
        logger.info(f"Tenant '{tenant}' created successfully.")

        if create_db:
            if not db_name:
                raise ValueError(f"Must provide `db_name` to create new database")
            self.create_new_db(db_name, tenant)

        return chromadb.HttpClient(
            host=env_config.chroma_server_host, 
            port=env_config.chroma_server_port, 
            ssl=env_config.chroma_server_ssl, 
            tenant=tenant, database=db_name, 
            settings=settings
        )

    def get_chroma_client(self, tenant, use_server: bool = True):

        """
        Initialize Chroma in server mode by default and provide CHROMA_SERVER_HOST/PORT
        If you do not want to use an external server, set CHROMA_USE_SERVER=false; this will use ChromaDB persistent client mode
        """

        if use_server:
            logger.info(f"Using Chroma Server >> Host: {env_config.chroma_server_host}, Port: {env_config.chroma_server_port}")
            # Only use server mode if explicitly requested
            try:
                chroma_client = chromadb.HttpClient(
                    host=env_config.chroma_server_host, port=env_config.chroma_server_port, ssl=env_config.chroma_server_ssl, tenant=tenant
                )
            except chromadb.errors.NotFoundError:
                exception = traceback.format_exc()
                logger.error(f"Error: {exception}")
                logger.info(f"Creating new tenant `{tenant}`...")
                chroma_client = self.create_new_tenant(tenant, db_name=f"{tenant}_db")

        else:
            # Embedded, on-disk Chroma (recommended for local dev)
            logger.info(f"Not Using Chroma Server >> Host: {env_config.chroma_server_host}, Port: {env_config.chroma_server_port}")
            chroma_path = os.getenv("CHROMA_PATH", "./chroma_db")
            # For recent Chroma, 'path' is the kw. Older versions may use 'persist_directory'.
            try:
                chroma_client = chromadb.PersistentClient(path=chroma_path)
            except TypeError:
                chroma_client = chromadb.PersistentClient(persist_directory=chroma_path)

        return chroma_client

    def init_chroma(self, collection_name: str, tenant=DEFAULT_TENANT, task: str = "retrieve"):
        # use_server = os.getenv("CHROMA_USE_SERVER", "false").lower() in ("1", "true", "yes")
        logger.info(f"Initializing Chroma database...")
        try:
            chroma_client = self.get_chroma_client(tenant=tenant, use_server=env_config.chroma_use_server)

        except Exception as e:
            message = f"Error connecting to Chroma database for collection `{collection_name}`: {e}"
            logger.error(message)
            raise ChromaConnectionError(message)

        collection = chroma_client.get_or_create_collection(
            collection_name,
            embedding_function=None, # we are not passing an embedding_func here as we are handling embedding generation in generate_and_store_embeddings()
            metadata={"hnsw": "cosine"}
        )
        logger.info(f"Collection {task}d: {collection_name}")
        return collection
