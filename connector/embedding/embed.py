from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import List
import torch

class bgeEmbeddings:
    def __init__(
        self,
        emb_model_name_or_path, 
        batch_size=64,
        max_len=512,
        device='cuda',
        **kwargs
    ):
        # super().__init__(**kwargs)
        self.model = AutoModel.from_pretrained(
            emb_model_name_or_path,
            trust_remote_code=True
        ).half().to(device)
        self.tokenizer = AutoTokenizer.from_pretrained(
            emb_model_name_or_path,
            trust_remote_code=True
        )
        if 'bge' in emb_model_name_or_path:
            self.DEFAULT_QUERY_BGE_INSTRUCTION_ZH = "为这个句子生成表示以用于检索相关文章："
        else:
            self.DEFAULT_QUERY_BGE_INSTRUCTION_ZH = ""
        self.emb_model_name_or_path = emb_model_name_or_path
        self.device = device
        self.batch_size = batch_size
        self.max_len = max_len
        print("successful load embedding model")
    
    def compute_kernel_bias(self, vecs, n_components=384):
        """
            bertWhitening: https://spaces.ac.cn/archives/8069
            计算kernel和bias
            vecs.shape = [num_samples, embedding_size],
            最后的变换: y = (x + bias).dot(kernel)
        """
        mu = vecs.mean(axis=0, keepdims=True)
        cov = np.cov(vecs.T)
        u, s, vh = np.linalg.svd(cov)
        W = np.dot(u, np.diag(1 / np.sqrt(s)))
        return W[:, :n_components], -mu

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
            Compute corpus embeddings using a HuggingFace transformer model.
        Args:
            texts: The list of texts to embed.
        Returns:
            List of embeddings, one for each text.
        """
        num_texts = len(texts)
        texts = [t.replace("\n", " ") for t in texts]
        sentence_embeddings = []

        for start in range(0, num_texts, self.batch_size):
            end = min(start + self.batch_size, num_texts)
            batch_texts = texts[start:end]
            encoded_input = self.tokenizer(batch_texts, max_length=512, padding=True, truncation=True,
                                           return_tensors='pt').to(self.device)

            with torch.no_grad():

                model_output = self.model(**encoded_input)
                # Perform pooling. In this case, cls pooling.
                if 'gte' in self.emb_model_name_or_path:
                    batch_embeddings = model_output.last_hidden_state[:, 0]
                else:
                    batch_embeddings = model_output[0][:, 0]

                batch_embeddings = torch.nn.functional.normalize(batch_embeddings, p=2, dim=1)
                sentence_embeddings.extend(batch_embeddings.tolist())

        # sentence_embeddings = np.array(sentence_embeddings)
        # self.W, self.mu = self.compute_kernel_bias(sentence_embeddings)
        # sentence_embeddings = (sentence_embeddings+self.mu) @ self.W
        # self.W, self.mu = torch.from_numpy(self.W).cuda(), torch.from_numpy(self.mu).cuda()
        return sentence_embeddings

    def embed_query(self, text: str) -> List[float]:
        """
            Compute query embeddings using a HuggingFace transformer model.
        Args:
            text: The text to embed.
        Returns:
            Embeddings for the text.
        """
        text = text.replace("\n", " ")
        if 'bge' in self.emb_model_name_or_path:
            encoded_input = self.tokenizer([self.DEFAULT_QUERY_BGE_INSTRUCTION_ZH + text], padding=True,
                                           truncation=True, return_tensors='pt').to(self.device)
        else:
            encoded_input = self.tokenizer([text], padding=True,
                                           truncation=True, return_tensors='pt').to(self.device)
        with torch.no_grad():
            model_output = self.model(**encoded_input)
            # Perform pooling. In this case, cls pooling.
            sentence_embeddings = model_output[0][:, 0]
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        # sentence_embeddings = (sentence_embeddings + self.mu) @ self.W
        return sentence_embeddings[0].tolist()

    