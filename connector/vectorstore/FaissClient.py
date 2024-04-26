

class FaissClient:
    def __init__(self, mode, user_id, kb_ids, *, threshold=1.1, client_timeout=3):
        self.user_id = user_id
        self.kb_ids = kb_ids
        if mode == 'local':
            self.host = MILVUS_HOST_LOCAL
        else:
            self.host = MILVUS_HOST_ONLINE
        self.port = MILVUS_PORT
        self.user = MILVUS_USER
        self.password = MILVUS_PASSWORD
        self.db_name = MILVUS_DB_NAME
        self.client_timeout = client_timeout
        self.threshold = threshold
        self.sess: Collection = None
        self.partitions: List[Partition] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.top_k = VECTOR_SEARCH_TOP_K
        self.search_params = {"metric_type": "L2", "params": {"nprobe": 256}}
        if mode == 'local':
            self.create_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 2048}}
        else:
            self.create_params = {"metric_type": "L2", "index_type": "GPU_IVF_FLAT", "params": {"nlist": 2048}}
        self.last_init_ts = time.time() - 100  # 减去100保证最初的init不会被拒绝
        self.init()

        # 混合检索
        self.hybrid_search = HYBRID_SEARCH
        if self.hybrid_search:
            self.index_name = [f"{user_id}++{kb_id}" for kb_id in kb_ids]
            self.client = ElasticsearchClient(index_name=self.index_name)