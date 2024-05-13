import pandas as pd
import time
from connector.embedding.embed import bgeEmbeddings
import chromadb
from tqdm import tqdm

# 加载 embedding 模型     
embed_model = bgeEmbeddings(
    '/root/autodl-tmp/One_Month_Paper/model/bge-large-en-v1.5', 
    batch_size=64,
    max_len=512,
    device='cuda:0'
)

# 加载 chroma 数据库 
client = chromadb.Client()
collection = client.create_collection(name="test_collection")

search_latency_fmt = "search latency = {:.4f}s"

# 读取数据
print("开始读取数据......")
# csv_df = pd.read_csv("datas/train.csv")  # 读取训练数据
# csv_data = csv_df.loc[:15]
# 加载 数据集 
csv_data = pd.read_csv('/root/autodl-tmp/One_Month_Paper/connector/vectorstore/data/merged_data.csv')
print(csv_data.shape)  # (476066, 3)

num_entities = len(csv_data)
print(num_entities)

print("开始插入向量数据......")

start_time = time.time()
for index, row in tqdm(csv_data.iterrows(), total=num_entities, desc="Processing DataFrame"):
    result = embed_model.embed_documents([row['Abstraction']])
    collection.add(
        documents=[row['Abstraction']],
        embeddings=[result[0]],
        metadatas=[{"title": row['title'], "author": row['author'], "subject": row['subject']}],
        ids=[str(row['id'])]
    ) 
end_time = time.time()
print(search_latency_fmt.format(end_time - start_time))
print("查看索引数据：")

# 保存



print("开始查询")
while True:
    search_sen = input("请输入查询语句：")
    search_vec = embed_model.embed_query(search_sen)
    start_time = time.time()
    search_res = collection.query(
        query_embeddings=[search_vec],
        n_results=7,
    )
    end_time = time.time()
    result = [{"ids": search_res["ids"][0][i], "meta": search_res["metadatas"][0][i], "doc": search_res["documents"][0][i]} for i in range(len(search_res["ids"][0]))]
    for it in result:
        print(it["ids"] + "   " + it["meta"][:4]+"...    "+it["doc"][:10]+"...")
    # print(result)
    print(search_latency_fmt.format(end_time - start_time))

# 单独加载
# index = faiss.read_index('vectors_file/faiss.index')
# search_vec = np.array(search_vec)
# topK = 3
# start_time = time.time()
# D, I = index.search(search_vec, topK)
# end_time = time.time()
# print(D)
# print(I)
# print(search_latency_fmt.format(end_time - start_time))

'''向量规模：476066；向量插入速度：1s，平均查询速度：130ms
请输入查询语句：
0         是的，我想一个洞穴也会有这样的问题
1          我认为洞穴可能会有更严重的问题。
110556       在这些洞穴里事情可能会变糟。
Name: sentences, dtype: object
search latency = 0.1315s
'''