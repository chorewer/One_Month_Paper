import sys
sys.path.append('/root/autodl-tmp/One_Month_Paper')
from connector.vectorstore import chroma_server
import pandas as pd
from connector.embedding.embed import bgeEmbeddings
from tqdm import tqdm
if __name__ == "__main__":
    # 读取 CSV 文件
    df = pd.read_csv('/root/autodl-tmp/One_Month_Paper/connector/vectorstore/data/merged_data.csv')
    
    embed_model = bgeEmbeddings(
        '/root/autodl-tmp/One_Month_Paper/model/bge-large-en-v1.5', 
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
    
    
