from langchain.schema import Document
from connector.vectorstore import chroma_server
from connector.embedding.embed import bgeEmbeddings

class Retriever:
    def __init__(self):
        self.emb_model = bgeEmbeddings(
            '/root/autodl-tmp/One_Month_Paper/model/bge-large-en-v1.5', 
            batch_size=64,
            max_len=512,
            device='cuda:0'
        )
        self.db = chroma_server.arXivDB()
        self.collection = self.db.collection
        self.temp_collection = self.db.tempCollection

    def retrieval_with_paras(
        self,
        query:str,
        topk:int,
    ):
        search_res = list()
        query_embeddings = self.emb_model.embed_query(query)
        search_res = self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=topk,
        )
        result = [{
            "ids": search_res["ids"][0][i], 
            "meta": search_res["metadatas"][0][i], 
            "doc": search_res["documents"][0][i]} 
                  for i in range(len(search_res["ids"][0]))
            ]
        return result
    def retrieval(self, query, methods=None):
        search_res = list()
        query_embeddings = self.emb_model.embed_query(query)
        search_res = self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=7,
        )
        result = [{"ids": search_res["ids"][0][i], "meta": search_res["metadatas"][0][i], "doc": search_res["documents"][0][i]} for i in range(len(search_res["ids"][0]))]
        return result
    
    def retrieval_in_temp(self,query,methods=None):
        search_res = list()
        query_embeddings = self.emb_model.embed_query(query)
        search_res = self.temp_collection.query(
            query_embeddings=[query_embeddings],
            n_results=7,
        )
        result = [{"ids": search_res["ids"][0][i], "meta": search_res["metadatas"][0][i], "doc": search_res["documents"][0][i]} for i in range(len(search_res["ids"][0]))]
        return result
    
    def retrieval_in_temp_with_para(self,query,methods=None,topk=None):
        search_res = list()
        query_embeddings = self.emb_model.embed_query(query)
        search_res = self.temp_collection.query(
            query_embeddings=[query_embeddings],
            n_results=topk,
        )
        result = [{"ids": search_res["ids"][0][i], "meta": search_res["metadatas"][0][i], "doc": search_res["documents"][0][i]} for i in range(len(search_res["ids"][0]))]
        return result
