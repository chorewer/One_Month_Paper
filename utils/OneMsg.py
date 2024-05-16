from typing import List


class OneMsg:
    role:str
    text:str
    context:List = None # [{ids:"",title:"",authors:"",content:"",pdf:bool,child:[{}]]
    # pdf:bool
    def __init__(self,role,text,context):
        self.role = role
        self.text = text
        self.context = context
        # self.pdf = pdf
        
    def parseList2ListPiece(self):
        role = self.role
        content = self.parseContext()
        return {
            "role" : role,
            "content" : content
        }
    
    def parseContext(self):
        header = "Info based On:\n"
        sub_header = ""
        ids = ""
        title = ""
        author = ""
        content = ""
        childs = ""
        for k,it in enumerate(self.context):
            sub_header = "The No" + str(k) + "paper \n"
            ids = "Paper ids " + it['ids'] + " \n"
            title = "Paper title " + it['title'] + " \n"
            author = "Author : " + it["authors"] + " \n"
            content = it["content"] + "\n"
            for t in it["child"]:
                childs += t + "\n"
        return header + sub_header + ids + title + author + content + childs
        