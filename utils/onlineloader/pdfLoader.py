import os
import threading
import requests
from utils.pdfs.mainPdfReader import mainPdfReader 
from connector.vectorstore.chroma_server import arXivDB
from connector.embedding.embed import bgeEmbeddings
from typing import List

class pdfLoader:
    def __init__(self, DB:arXivDB,emb_model:bgeEmbeddings) -> None:
        self.urlBase = r"https://arxiv.org/pdf/"
        self.save_path = r"tmp"
        self.db = DB
        self.emb_model = emb_model
        
    def load_pdf_doc(self, arxiv_id:str):
        filename = arxiv_id + ".pdf"
        self.downLoad(filename=filename)
        rd = mainPdfReader(self.os.path.join(self.save_path,filename))
        rd.main_call()
        for i,it in enumerate(rd.data):
            result = self.embed_model.embed_documents([it])
            self.db.tempCollection.add(
                documents=[it],
                embeddings=[result[0]],
                metadatas=[{"from": arxiv_id}],
                ids=[arxiv_id+"'s--"+str(i)]
            ) 
        
    
    def downLoad(self, filename):
        url = self.urlBase + filename
        
        self.download_file(url_of_file=url, name=os.path.join(self.save_path,filename),number_of_threads=1) 

    def Handler(self, start, end, url, filename): 
        # specify the starting and ending of the file 
        headers = {'Range': 'bytes=%d-%d' % (start, end)} 
        # request the specified part and get into variable     
        r = requests.get(url, headers=headers, stream=True) 
        # open the file and write the content of the html page into file. 
        with open(filename, "r+b") as fp: 
            fp.seek(start) 
            var = fp.tell() 
            fp.write(r.content)

    def download_file(self,url_of_file,name,number_of_threads): 
        r = requests.head(url_of_file) 
        if name: 
            file_name = name 
        else: 
            file_name = url_of_file.split('/')[-1] 
        try: 
            file_size = int(r.headers['content-length']) 
        except: 
            print("Invalid URL")
            return

        part = int(file_size) / number_of_threads 
        fp = open(file_name, "wb") 
        fp.close() 
        for i in range(number_of_threads): 
            start = int(part * i) 
            end = int(start + part) 
            # create a Thread with start and end locations 
            t = threading.Thread(target=self.Handler, 
                kwargs={'start': start, 'end': end, 'url': url_of_file, 'filename': file_name}) 
            t.setDaemon(True) 
            t.start() 

        main_thread = threading.current_thread() 
        for t in threading.enumerate(): 
            if t is main_thread: 
                continue
            t.join() 

    