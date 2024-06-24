
from connector.vectorstore import chroma_server
import pandas as pd
from connector.embedding.embed import bgeEmbeddings
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()
os_embed_directory = os.getenv("EMBED_DIRECTORY")
if __name__ == "__main__":
    # 读取 CSV 文件
    df = pd.read_csv('data/merged_data.csv')
    
    embed_model = bgeEmbeddings(
        os_embed_directory, 
        batch_size=64,
        max_len=512,
        device='cuda:0'
    )
    
    DB = chroma_server.arXivDB()
    
    collection = DB.collection
    
    total_len = len(df)
    for index, row in tqdm(df.iterrows(), total=total_len, desc="Processing DataFrame"):
        result = embed_model.embed_documents([row['Abstraction']])
        collection.add(
            documents=[row['Abstraction']],
            embeddings=[result[0]],
            metadatas=[{"title": row['title'], "author": row['author'], "subject": row['subject']}],
            ids=[str(row['id'])]
        ) 
        pass  #
    
    
