import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class Reranker:
    def __init__(self, device='cuda'):
        self.rerank_tokenizer = AutoTokenizer.from_pretrained('/root/autodl-tmp/One_Month_Paper/model/bge-reranker-large')
        self.rerank_model = AutoModelForSequenceClassification.from_pretrained('/root/autodl-tmp/One_Month_Paper/model/bge-reranker-large')\
            .half().to(device).eval()
        self.device = device
        print('successful load rerank model')

    def rerank(self, docs, query, k=5):
        pairs = []
        for d in docs:
            pairs.append([query, d['doc']])
        with torch.no_grad():
            inputs = self.rerank_tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)\
                .to(self.device)
            scores = self.rerank_model(**inputs, return_dict=True).logits.view(-1, ).float().cpu().tolist()
        docs = [(docs[i], scores[i]) for i in range(len(docs))]
        docs = sorted(docs, key = lambda x: x[1], reverse = True)
        docs_ = []
        for item in docs:
            docs_.append(item[0])
        return docs_[:k]