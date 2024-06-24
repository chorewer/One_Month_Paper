import sys
# sys.path.append('/root/autodl-tmp/One_Month_Paper')
import os
import threading
import requests
from utils.pdfs.mainPdfReader import mainPdfReader 
from connector.vectorstore.chroma_server import arXivDB
from connector.embedding.embed import bgeEmbeddings
from typing import List
import asyncio
import aiohttp

class pdfLoader:
    def __init__(self, DB:arXivDB,emb_model:bgeEmbeddings) -> None:
        self.urlBase = r"https://arxiv.org/pdf/"
        self.save_path = r"tmp"
        self.db = DB
        self.emb_model = emb_model
        
    def load_pdf_doc(self, arxiv_id:str):
        print("loading loding docc")
        filename = arxiv_id + ".pdf"
        # self.downLoad(filename=filename)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.downLoad(arxiv_id=arxiv_id))
        rd = mainPdfReader(os.path.join(self.save_path,filename))
        rd.main_call()
        print("embedding of the pdfs "+filename)
        for i,it in enumerate(rd.data):
            result = self.emb_model.embed_documents([it])
            self.db.tempCollection.add(
                documents=[it],
                embeddings=[result[0]],
                metadatas=[{"from": arxiv_id}],
                ids=[arxiv_id+"'s--"+str(i)]
            ) 
        print("successfully load in the pdf" + filename)
        loop.close()
        return True
        
    
    async def downLoad(self,arxiv_id):
        url = self.urlBase + arxiv_id
        filename = arxiv_id + ".pdf"
        await self.download_file(url_of_file=url, name=os.path.join(self.save_path,filename),number_of_threads=1) 
        
        
 
    async def download_part(self, session, start, end, url, filename):
        headers = {'Range': f'bytes={start}-{end}'}
        async with session.get(url, headers=headers) as response:
            chunk = await response.read()
            with open(filename, 'ab') as f:
                f.write(chunk)

    async def download_file(self, url_of_file, name, number_of_threads):
        async with aiohttp.ClientSession() as session:
            r = await session.head(url_of_file)
            file_name = name
            try:
                file_size = int(r.headers['Content-Length'])
            except:
                print("Invalid URL")
                return

            part = int(file_size) / number_of_threads
            fp = open(file_name, "wb")
            fp.close()

            tasks = []
            for i in range(number_of_threads):
                start = int(part * i)
                end = int(start + part)
                tasks.append(self.download_part(session, start, end, url_of_file, file_name))

            await asyncio.gather(*tasks)


async def main():
    downloader = pdfLoader()
    save_path = r"tmp"
    filename = r"2401.12599.pdf"
    await downloader.download_file(r"https://arxiv.org/pdf/2405.05218", name=os.path.join(save_path,filename), number_of_threads=1)

if __name__ == "__main__":
    asyncio.run(main())