

embedding_client = EmbeddingClient(
    server_url=LOCAL_EMBED_SERVICE_URL,
    model_name=LOCAL_EMBED_MODEL_NAME,
    model_version='1',
    resp_wait_s=120,
    tokenizer_path='qanything_kernel/connector/embedding/embedding_model_0630'
)

class bgeEmbeddings:
    
    def __init__(self):
        pass

    def _get_embedding(self, queries):
        embeddings = embedding_client.get_embedding(queries, max_length=LOCAL_EMBED_MAX_LENGTH)
        return embeddings


    def _get_len_safe_embeddings(self, texts: List[str]) -> List[List[float]]:
        all_embeddings = []
        batch_size = LOCAL_EMBED_BATCH

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                future = executor.submit(self._get_embedding, batch)
                futures.append(future)
            debug_logger.info(f'embedding number: {len(futures)}')
            for future in tqdm(futures):
                embeddings = future.result()
                all_embeddings += embeddings
        return all_embeddings