

class Retriever:
    def __init__(self, emb_model_name_or_path=None, corpus=None, device='cuda', lan='zh'):
        self.device = device
        self.langchain_corpus = [Document(page_content=t) for t in corpus]
        self.corpus = corpus
        self.lan = lan
        if lan=='zh':
            tokenized_documents = [jieba.lcut(doc) for doc in corpus]
        else:
            tokenized_documents = [doc.split() for doc in corpus]
        self.bm25 = BM25Okapi(tokenized_documents)

        self.emb_model = TextEmbedding(emb_model_name_or_path=emb_model_name_or_path)
        self.db = FAISS.from_documents(self.langchain_corpus, self.emb_model)