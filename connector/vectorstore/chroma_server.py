import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
import os

load_dotenv()
os_persist_directory = os.getenv("PERSIST_DIRECTORY")

class arXivDB:
    persist_directory = os_persist_directory
    def __init__(self):
        
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
                # chroma_db_impl="duckdb+parquet",
        )
        self.collection = self.client.get_or_create_collection(
            name="ARXIV"
        )
        self.tempClient = chromadb.Client()
        self.tempCollection = self.tempClient.get_or_create_collection(name="temp_collection")
        
        print("the collection scaled in :" + str(self.collection.count()))
    
    
if __name__=="__main__":
    db = arXivDB()
    