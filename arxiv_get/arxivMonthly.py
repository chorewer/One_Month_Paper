import asyncio
from bs4 import BeautifulSoup
import requests
import aiohttp
import time
import random
import re
import datetime
import os
import argparse
import pandas as pd
from tqdm import tqdm
import tenacity
from tqdm.asyncio import tqdm_asyncio

# Edit from translate import Translator
@tenacity.retry(wait=tenacity.wait_exponential(multiplier=2, min=4, max=10),
                    stop=tenacity.stop_after_attempt(5),
                    reraise=True)
async def get_one_page(url,session):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
        }
        async with session.get(url,headers=headers) as response:
            # print(url)
            # print("get Response" + url)
            if response.status == 200:
                # print("Successfully access " + url + "!")
                result = await response.text()
                return result
            else:
                print(response.status)
                raise Exception
    except:
        raise Exception
    return None

async def Handle(href,meta_node,session,sem):
    async with sem: 
        await asyncio.sleep(3)
        new_html = await get_one_page(href,session)
        new_soup = BeautifulSoup(new_html, features="html.parser").find("blockquote")
        meta_node.append(new_soup)

async def accessMonthlyPaper(data_dir, categories, months):
    for category in categories:
        for month in months:
            url = "https://arxiv.org/list/" + category + "/" + month
            print("accessing " + category + " in " + month)
            conn = aiohttp.TCPConnector(limit=1)
            async with aiohttp.ClientSession(connector=conn) as session: 
                html = await get_one_page(url,session)
                soup = BeautifulSoup(html, features="html.parser")
                print("Got First Page")
                print("access to "+ url)
                # get the url that contains all paper in the specific category and month
                numofpaper = int(re.findall(r'total of (\d+) entries:',soup.findAll("small")[0].text)[0])
                print("This Term Has Paper Num of "+str(numofpaper))
                if (numofpaper > 25 and numofpaper <= 2000):
                    allurl = (
                        "https://arxiv.org/"
                        + soup.findAll("a", attrs={"href": re.compile("\?show=")})[0]["href"]
                    )
                    html = await get_one_page(allurl,session)
                    soup = BeautifulSoup(html, features="html.parser")
                    print("Got All Page")
                elif ( numofpaper > 2000 ):
                    nowMax = 0
                    temp_soup = BeautifulSoup("", features="html.parser")
                    while (nowMax < numofpaper):
                        theNow = nowMax + 1
                        nowMax += 2000
                        if (nowMax > numofpaper):
                            nowMax = numofpaper
                        allurl = url + "?skip="+str(theNow)+"&show="+str(nowMax)
                        new_html = await get_one_page(allurl,session)
                        new_soup = BeautifulSoup(new_html, features="html.parser")
                        temp_soup.extend(new_soup)
                        print(str(theNow) + " to "+str(nowMax)+" Got !")
                    soup = temp_soup
                    
                # get abstract
                all_abs = soup.findAll("a", title="Abstract")
                all_metas = soup.findAll("div",class_="meta")
                href_attributes = [
                    f"https://arxiv.org/{link['href']}" 
                    for link in all_abs]
                sem = asyncio.Semaphore(5)
                tasks = [Handle(href_attributes[i],all_metas[i],session,sem) for i in range(len(all_abs))]
                await tqdm_asyncio.gather(*tasks)
            
            now_time = datetime.datetime.now().strftime("%y%m%d")
            # create month folders
            page_dir = os.path.join(data_dir + "/" + month + "_until_" + now_time + "/")
            if not os.path.exists(page_dir):
                os.mkdir(page_dir)
            page_name = category + ".html"
            with open(os.path.join(page_dir + page_name), "w", encoding="utf-8") as fp:
                fp.write(soup.prettify())

def generatePaperList(data_dir, categories, months):
    # translator= Translator(to_lang="chinese")
    for month in months:
        for dirpath, _, filenames in os.walk(data_dir):
            # find the month folders
            if dirpath.find(month) != -1:
                for category in categories:
                    page_name = category + ".html"
                    # not exist html file for the category in this month
                    if page_name not in filenames:
                        print("No " + category + " in " + month)
                        continue
                    with open(
                        os.path.join(dirpath, page_name), "r", encoding="utf-8"
                    ) as f:
                        page = f.read()
                        soup = BeautifulSoup(page, features="lxml")
                        content = soup.dl
                        ids = content.find_all("a", title="Abstract")
                        titles = content.find_all("div", class_="list-title mathjax")
                        authors = content.find_all("div", class_="list-authors")
                        subjects = content.find_all("div", class_="list-subjects")
                        abstracts = content.find_all("blockquote")
                        items = []
                        print(
                            "total papers for "
                            + category
                            + " in "
                            + month
                            + ":"
                            + str(len(ids))
                        )
                        for _, paper in tqdm(
                            enumerate(zip(ids, titles, authors, subjects, abstracts))
                        ):
                            items.append(
                                [
                                    paper[0]
                                    .text.replace("arXiv:", "")
                                    .replace("\n", " ")
                                    .strip(),
                                    paper[1]
                                    .text.replace("Title:", "")
                                    .replace("\n", " ")
                                    .strip(),
                                    paper[2]
                                    .text.replace("Authors:", "")
                                    .replace("\n        ", "")
                                    .replace("\n", "")
                                    .strip(),
                                    paper[3]
                                    .text.replace("Subjects:", "")
                                    .replace("\n         ", "")
                                    .replace("\n        ", "")
                                    .replace("\n", ""),
                                    paper[4]
                                    .text.replace("Abstract:","")
                                    .replace("\n", " ")
                                    .strip(),
                                ]
                            )
                        # all paper
                        name = ["id", "title", "author", "subject", "Abstraction"]
                        paper = pd.DataFrame(columns=name, data=items)
                        # paper_no_duplicate = paper.drop_duplicates(subset=['id'])
                        paper.to_csv(os.path.join(dirpath, category + ".csv"))
                        print("Saved paperlist for " + category + " in " + month)

def All_in_One(data_dir):

    # 初始化一个空的 DataFrame 来存储所有数据
    all_data = pd.DataFrame()

    # 遍历目录下的所有文件
    for filename in tqdm(os.listdir(data_dir)):
        if filename.endswith(".csv"):
            # 构造文件的完整路径
            file_path = os.path.join(data_dir, filename)
            
            # 读取 CSV 文件
            data = pd.read_csv(file_path)
            
            # 将读取的数据添加到all_data中
            all_data = pd.concat([all_data, data], ignore_index=True)

    print("begin drop duplicates")
    # 对合并后的数据进行去重，保留第一个出现的 id
    all_data.drop_duplicates(subset=['id'], keep='first', inplace=True)

    # 将合并后的数据保存为一个 CSV 文件
    output_file = 'merged_data.csv'
    all_data.to_csv(output_file, index=False)

    print(f"合并后的数据已保存到 {output_file} 文件中。")
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Custom your own areas and times")
    parser.add_argument("--operation", type=str, default="access", help="months list")
    parser.add_argument(
        "--months", type=str, nargs="+", default=["2207"], help="months list"
    )
    parser.add_argument(
        "--categories",
        type=str,
        nargs="+",
        default=["cs.AI", "cs.PL", "cs.SE"],
        help="categories list,you can choose from https://arxiv.org/archive/cs",
    )
    parser.add_argument(
        "--keywords", type=str, nargs="+", help="keywords for filter operation"
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default="./",
        help="data path for saving all the output files",
    )
    args = parser.parse_args()
    print(args)
    if not os.path.exists(args.data_dir):
        os.mkdir(args.data_dir)
    if args.operation == "access":
        asyncio.run(accessMonthlyPaper(args.data_dir, args.categories, args.months))
    elif args.operation == "generate":
        generatePaperList(args.data_dir, args.categories, args.months)
    elif args.operation == "merge":
        All_in_One(args.data_dir)
