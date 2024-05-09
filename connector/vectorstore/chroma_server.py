import chromadb
from chromadb.config import Settings

class arXivDB:
    persist_directory = "/root/autodl-tmp/One_Month_Paper/connector/vectorstore/chromadb_data"
    def __init__(self):
        
        self.client = chromadb.PersistentClient(
            # Settings(
            path=self.persist_directory,
                # chroma_db_impl="duckdb+parquet",
            # )
        )
        self.collection = self.client.get_or_create_collection(
            name="ARXIV"
        )
        self.tempClient = chromadb.Client()
        self.tempCollection = self.tempClient.get_or_create_collection(name="temp_collection")
        
        print("the collection scaled in :" + str(self.collection.count()))
    
    
if __name__=="__main__":
    db = arXivDB()
    