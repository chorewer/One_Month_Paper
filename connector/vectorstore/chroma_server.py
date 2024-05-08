import chromadb
from chromadb.config import Settings

class arXivDB:
    persist_directory = "chromadb_data"
    def __init__(self):
        
        self.client = chromadb.Client(
            Settings(
                persis_directory=self.persist_directory,
                chroma_db_impl="duckdb+parquet",
            )
        )
        self.collection = self.client.get_or_create_collection(
            name="ARXIV"
        )