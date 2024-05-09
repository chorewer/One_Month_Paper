import pdfplumber
from PyPDF2 import PdfReader
import fitz
from tqdm import tqdm
import nltk

# nltk.download('punkt') 

class mainPdfReader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.data = []
        
    # TODO pdf 总体上去 提取 文字，但是仍需要忽略表格和图片
    def Extract_RawText(self, max_seq = 512, min_len = 6):
        all_content = ""
        for idx, page in enumerate(PdfReader(self.pdf_path).pages):
            page_content = ""
            text = page.extract_text()
            words = text.split("\n")
            for idx, word in enumerate(words):
                text = word.strip().strip("\n")
                if("...................." in text or "目录" in text):
                    continue
                if(len(text) < 1):
                    continue
                if("! !" in text):
                    continue
                if(text.isdigit()):
                    continue
                page_content = page_content + text
            if(len(page_content) < min_len):
                continue
            all_content = all_content + page_content
        return all_content
    
    def Sentence_By_NLTK(self,text):
        sentences = nltk.sent_tokenize(text)
        return sentences
    
    def SlidingWindow(self, sentences, kernel = 512, stride = 1):
        # sz = len(sentences)
        cur = ""
        fast = 0
        slow = 0
        while(fast < len(sentences)):
            sentence = sentences[fast]
            if(len(cur + sentence) > kernel and (cur + sentence) not in self.data):
                self.data.append(cur + sentence + ". ")
                cur = cur[len(sentences[slow] + ". "):]
                slow = slow + 1
            cur = cur + sentence + "。"
            fast = fast + 1

    def main_call(self):
        text = self.Extract_RawText()
        sentences = self.Sentence_By_NLTK(text)
        self.SlidingWindow(sentences=sentences)
    

if __name__ == "__main__":
    rd = mainPdfReader(r"G:\1ALPFtask\One_Month_Paper\utils\pdfs\2404.10981v1.pdf")
    text = rd.Extract_RawText()
    sentences = rd.Split_By_NLTK(text)
    print(sentences)
    pass