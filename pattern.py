# TODO 运行多种模式来判断 
#     -问题增强 
#         - 生词转换 
#         - 备选答案 
#     - 意图判断 
#     - 模糊检索（条件） 搜索符合的信息 
#         - 条件模糊搜索 
#     - 精确检索（条件） 查询某个文本的具体定义等等
#     - 寻找解决方案 
#     - 文档概括 对整个库的信息进行概述等 
from typing import List
from connector.llm.llm_online import QwenLLM
from core.retriever import Retriever
from core.reranker import Reranker
from utils.onlineloader.pdfLoader import pdfLoader
import json

class Pattern:
    def __init__(self,llm:QwenLLM,retriever:Retriever,reranker:Reranker,online: pdfLoader):
        self.llm = llm
        self.retriever = retriever
        self.reranker = reranker
        self.online = online
        pass
    
    def intention_recognition(self,query,history):
        input_his = []
        for it in history :
            input_his.append(it.parseList2ListPiece())
        template = self.intention_template().format(query)
        result = self.llm.simple_call(input=template,history=input_his)
        return result
    
    # 名词 解释 原query => 结果list 
    def make_noun_interpretation(self,query:str)->List:
        template = self.proper_noun_interpretation().format(query)
        result = self.llm.simple_call_without_history(input=template)
        result_list = json.loads(result)
        return result_list

    # 问题提升 => 问题上下文列表
    def query_aug_main(self,query:str):
        query_for_abs_list = self.make_noun_interpretation(query=query)
        context_list = []
        for i,it in enumerate(query_for_abs_list):
            explanation = self.make_precise_explanation(it)
            context_list.extend(explanation)
        return query_for_abs_list,context_list
    
    # 名词 的 精确解释 （无历史） 
    def make_precise_explanation(self,query:str):
        context_list = self.make_retrieve_and_rerank(query=query,first_recall=5,last_recall=2)
        context = self.generate_context_num(2,[it['doc'] for it in context_list])
        input = self.precise_explanation_template().format(query,context)
        result = self.llm.simple_call_without_history(input=input)
        return result
    
    # 问题的检索 + 重排 pipeline 
    def make_retrieve_and_rerank(self,query:str,first_recall:int,last_recall:int):
        list = self.retriever.retrieval_with_paras(query=query,topk=first_recall)
        list = self.reranker.rerank(list,query=query,k=last_recall)
        return list
    # list : [["ids":"","meta":"","doc":""]]

    #简单 no history 问答 
    def make_response_no_history(self,query:str,data:list):
        list_just_doc = [it['doc'] for it in data]
        context = self.generate_context_num(list_just_doc.count,list_just_doc)
        prompt = self.baseline_template().format(query,context)
        result = self.llm.simple_call_without_history(input = prompt)
        return result
    
    #简单带历史 history 问答
    def make_response_history(self,query:str,data:list,history,rag:bool):
        list_just_doc = [it['doc'] for it in data]
        context = ""
        if len(list_just_doc) > 0:
            context = self.generate_context_num(list_just_doc.count,list_just_doc)
        
        # context = ""
        # if len(list_just_doc) > 0:
        #     context = self.generate_context_num(list_just_doc.count,list_just_doc)  
        prompt = self.baseline_template().format(query,context)
        print(prompt)
        input_his = []
        for it in history :
            input_his.append(it.parseList2ListPiece())
            
        result = self.llm.simple_call(input=prompt,history=input_his)
        
        remove_str = ""
        if rag:
            remove_prompt = self.remove_template().format(query,result,context)
            remove_str = self.llm.simple_call_without_history(input=remove_prompt)
            print(remove_str)
            remove_list = json.loads(remove_str)
            print(remove_list)
            for it in reversed(remove_list):
                if len(list_just_doc) > 0:
                    list_just_doc.pop(int(it))
            # print(len(list_just_doc))
            
        return result,remove_list
    
    # 文档的录入
    def document_in_pdf(self,doc_id):
        print("document in pdf")
        return self.online.load_pdf_doc(doc_id)
        # print("successful load")
    
    # 内db查询 
    def inner_search(self,query:str):
        # self.make_retrieve_and_rerank(query,7,3)
        list = self.retriever.retrieval_in_temp_with_para(query=query,topk=7)
        if len(list)> 3:
            list = self.reranker.rerank(list,query,3)
        return list
    
    # 以下都是 提示词 template 
    def precise_explanation_template():
        template = "Please provide a answer for this question:{}\n" \
            "Based on the provide context:{}"
        return template
    
    def proper_noun_interpretation(self):
        template =  "Please select the key and unknown abbreviations, abbreviations, and proper names in the question\n" \
                    "question: {}\n" \
                    "first, to generate questions about those words. \n" \
                    "Second, wrap them in a JSON-formatted list. \n" \
                    "Third, simply print the list in the output, such as [\"What is eRAG\"] \n"
        # bge embedding 经过针对问句的嵌入微调
        return template

    def query_augment_template(self):
            prompt_template = "the question is : {} \n"\
                "preliminary context is :{} \n "\
                "For the provided preliminary context, generate all reasonable answers \n "
            #preliminary context 来自名词、专有名词解释，得到的备选答案将一并纳入
            return prompt_template

    def augmented_template(self):
        template = "You are an accurate and reliable AI assistant able to answer user questions with the help of external documentation, be aware that external documentation may contain noisy factual errors." \
            "If the information in the document contains the correct answer, you will answer accurately."\
            "If the information in the document does not contain the answer, you will generate 'There is not enough information in the document, so I cannot answer that question based on the document provided.'" \
            "If a part of the document contains an error that is not consistent with the facts, please answer 'The document provided has a factual error.'And generate the correct answer." \
            "The question, noun explanation, and relevant context are given below\n" \
            "```\nquestion : {}\n" \
            "```\nrelevant context :{}\n"
        return template
    
    # 将问题列 的text 放入 模板当中形成string
    def generate_context_num(self,num:int,text:List):
        context = "" 
        for i,p in enumerate(text):
            context += "Here's the No." + str(i)+" external document:\n"
            context += p + "\n"
        return context
        
    def baseline_template(self):
            template = "You are an accurate and reliable AI assistant able to answer user questions with the help of external documentation and history message, be aware that external documentation may contain noisy factual errors." \
                            "If the information in the document contains the correct answer, you will answer accurately."\
                            "If the information in the document does not contain the answer, you will generate 'There is not enough information in the document, so I cannot answer that question based on the document provided.'" \
                            "If a part of the document contains an error that is not consistent with the facts, please answer 'The document provided has a factual error.'And generate the correct answer." \
                            "Given relevant external documentation, answer user questions based on it and history message." \
                            "user question: \n---" \
                            "{}\n" \
                            "Some external documents can be answered in descending order of priority by summarizing their information:" \
                            "{}\n"
            return template
    
    # paper 粒度的删除 
    def remove_template(self):
        template = "Indicate which document does not contribute to the answer" \
            "Just include a list of int in python format in the output. for example, [0,2] means the first and third paper is no use for answer \n" \
            "The Question is : {} " \
            "The generated answer is : {} " \
            "The document is on below : \n {} \n"
            
        return template

    # 意图识别
    def intention_template(self):
        template = "Your output can be only yes or no , do not output any other text and Punctuation marks." \
            "You need to determine the intent of the question : {} " \
            "If the question is intended to lead to further discussion based on something in the historical question answering, you need to output no.\n" \
            "If the question is about something new, you need to output yes."
        return template
    
client = QwenLLM()
retriver = Retriever()
reranker = Reranker()
online = pdfLoader(retriver.db,retriver.emb_model)
# 模式处理
pattern = Pattern(client,retriever=retriver,reranker=reranker,online=online)

def return_pattern():
    return pattern