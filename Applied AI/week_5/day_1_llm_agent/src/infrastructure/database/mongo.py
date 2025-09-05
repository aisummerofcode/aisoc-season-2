import logging
from src.config.appconfig import env_config
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MongoDBClientConfig:
    def __init__(self):
        try:
            logging.info("intializing MongoDB connection...")
            context_uri = env_config.mongo_conn_url
            self.context_client = MongoClient(context_uri, serverSelectionTimeoutMS=5000)

            database_name = env_config.mongo_database_name

            self.context_db = self.context_client[database_name]

            collection_name = 'aichatmemory'
            self.context_collection=None
            self._setup_collection(collection_name)
            
            logger.info("🎉 MongoDB initialization completed successfully!")

        except ConnectionFailure as cf:
            logger.error(f"Connection failure >>> {cf}")
            raise

        except ServerSelectionTimeoutError as st:
            logger.error(f"Server Timeout error failure >>> {st}")
            raise

    def _setup_collection(self,collection_name):
        try:
            existing_collections = self.context_db.list_collection_names()
            logger.info(f"Found {len(existing_collections)} existing collections in the db")
            if collection_name not in existing_collections:
                self.context_db.create_collection(collection_name)
            else:
                logger.info(f"{collection_name} already exists in the db")
            
            self.context_collection = self.context_db[collection_name]

        except Exception as e:
            print(e)

    def get_context_db(self):
        return self.context_db

    def get_context_collection(self):
        return self.context_collection

    def close_connection(self):
        try:
            if hasattr(self,'context_client'):
                self.context_client.close()
        except Exception as e:
            print(e)