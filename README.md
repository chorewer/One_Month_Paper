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

# TODO

1、完善多类型知识库读取，目前只展示了一个 PDF 示例

2、加入检索器与重排器微调，提高效果

3、加入检索、重排、RAG 评价指标，展示各个模型与流程的效果

4、显存与推理速度优化

5、RAG 方案优化
