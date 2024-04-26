from bs4 import BeautifulSoup
import requests
import time
import random
import re
import datetime
import os
import argparse
import pandas as pd
from tqdm import tqdm


#copy from repository : codingClaire / access-arxiv-paperlist
def get_one_page(url):
    response = requests.get(url)
    while response.status_code == 403:
        time.sleep(3000 + random.uniform(0, 500))
        response = requests.get(url)
        print(response.status_code)
    if response.status_code == 200:
        print("Successfully access " + url + "!")
        return response.text
    return None

# TODO Edit from repository : codingClaire / access-arxiv-paperlist
# to Get Abs/20xx.xx Page For Its Abstract
def accessMonthlyPaper(data_dir, categories, months):
    for category in categories:
        for month in months:
            url = "https://arxiv.org/list/" + category + "/" + month
            print("accessing " + category + " in " + month)
            html = get_one_page(url)
            soup = BeautifulSoup(html, features="html.parser")
            # get the url that contains all paper in the specific category and month
            allurl = (
                "https://arxiv.org/"
                + soup.findAll("a", attrs={"href": re.compile("\?show=")})[0]["href"]
            )
            html = get_one_page(allurl)
            soup = BeautifulSoup(html, features="html.parser")
            
            # get abstract
            all_abs = soup.findAll("a", title="Abstract")
            all_metas = soup.findAll("div",class_="meta")
            href_attributes = [
                f"https://arxiv.org/{link['href']}" 
                for link in all_abs]
            
            for i in range(len(all_abs)):
                new_html = get_one_page(href_attributes[i])
                new_soup = BeautifulSoup(new_html, features="html.parser").find("blockquote")
                all_metas[i].append(new_soup)
            
            now_time = datetime.datetime.now().strftime("%y%m%d")
            # create month folders
            page_dir = os.path.join(data_dir + "/" + month + "_until_" + now_time + "/")
            if not os.path.exists(page_dir):
                os.mkdir(page_dir)
            page_name = category + ".html"
            with open(os.path.join(page_dir + page_name), "w", encoding="utf-8") as fp:
                fp.write(soup.prettify())

#from repository : codingClaire / access-arxiv-paperlist
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
                            enumerate(zip(ids, titles, authors, subjects))
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
                                    "No Translation",
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
                                ]
                            )
                        # all paper
                        name = ["id", "title", "translation", "author", "subject"]
                        paper = pd.DataFrame(columns=name, data=items)
                        paper.to_csv(os.path.join(dirpath, category + ".csv"))
                        print("Saved paperlist for " + category + " in " + month)

