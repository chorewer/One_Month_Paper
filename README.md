# ArXiv RAG

本项目是从 arxiv 上获取数据，旨在快速搜索相关论文，并提供概括和多轮对话，旨在帮助论文的阅读

# 文件目录

```
.
├── arxiv_get
│   └──arxivMonthly.py # 论文数据爬取
├── connector # 主要模块连接
│   ├── embedding # 嵌入管理器
│   ├── llm # 大模型API管理器
│   └── vectorstore # 向量数据库管理器
├── core
│   ├── reranker # 重排器
│   └── retriever # 检索器
├── utils
│   ├── onlineloader # 文件下载管理
│   └── retriever # pdf解析器
├── requirement.txt # 示例环境
├── stream_lit.py # 主程序 UI环境
└── README.md # 本文件
```

# 安装
1. pip install -r requirements.txt 安装环境
3. 在项目根目录下新建model文件夹，在其中下载bge-large-en-v1.5和bge-reranker-large模型，文件较大，需要安装git lfs进行拉取
```
git clone https://www.modelscope.cn/AI-ModelScope/bge-large-en-v1.5.git
git clone https://www.modelscope.cn/Xorbits/bge-reranker-large.git
```
3. 在项目根目录下复制example.env,并重命名其为.env,配置其中的模型路径等
2. 运行connector/vectorstore/load_chroma.py,对向量数据库进行初始化
4. 在项目根目录下 执行 streamlit run streamlit 命令


# TODO

1、加入各种对话模式：禁用RAG只使用多轮对话，针对某篇文章进行RAG ，针对摘要广泛搜索等

2、加入搜索时加载过程中的可视化进度条

3、加入一个后台的更新功能，获取除24年1月份外其他的月份功能

4、加入自查询检索器，识别用户问题中某些元数据（作者，时间）对所检索文章进行限定

5、显存与推理速度优化
