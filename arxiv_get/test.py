import requests
import datetime

def query_arxiv_by_date(start_date, end_date):
    # 构建 API 请求 URL
    url = 'http://export.arxiv.org/api/query'
    
    # 构建查询参数
    query = f'date:[{start_date} TO {end_date}]'  # 使用查询语法指定日期范围
    params = {
        'search_query': query,
        'max_results': 10  # 指定返回结果的最大数量
    }
    
    # 发送请求并获取响应
    response = requests.get(url, params=params)
    
    # 解析响应并提取文章信息
    if response.status_code == 200:
        entries = response.text.split('<entry>')  # 切分每篇文章的信息
        for entry in entries[1:]:  # 第一个 entry 是空的
            title = entry.split('<title>')[-1].split('</title>')[0]  # 提取文章标题
            summary = entry.split('<summary>')[-1].split('</summary>')[0]  # 提取文章摘要
            print(f'Title: {title}')
            print(f'Summary: {summary}')
            print('-' * 50)
    else:
        print(f"Failed to fetch articles. Status code: {response.status_code}")

# 指定要查询的日期范围
start_date = '2024-01-01'
end_date = '2024-01-31'

# 执行查询
query_arxiv_by_date(start_date, end_date)
