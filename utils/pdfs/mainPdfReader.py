import pdfplumber
from PyPDF2 import PdfReader

class mainPdfReader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.data = []
    
    def GetHeader(self,page):
        try:
            lines = page.extract_text()
        except:
            return None
        print(lines)
        # return None
    def getAPage(self):
        # self.GetHeader(PdfReader(self.pdf_path).pages[0])
        # for i,page in enumerate(PdfReader(self.pdf_path).pages):
        #     self.GetHeader(page)
        # return pdf.pages[0]
        with pdfplumber.open(self.pdf_path) as pdf:
            print()
    def BlockParsing(self, max_seq = 1024):
        with pdfplumber.open(self.pdf_path) as pdf:
            for i,p in enumerate(pdf.pages):
                print(p)
            # return enumerate(pdf.pages)
    

if __name__ == "__main__":
    rd = mainPdfReader(r"/root/autodl-tmp/One_Month_Paper/utils/pdfs/2404.10981v1.pdf")
    print(rd.getAPage())
    pass