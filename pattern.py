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
import json

class Pattern:
    def __init__(self,llm:QwenLLM,retriever:Retriever,reranker:Reranker):
        self.llm = llm
        self.retriever = retriever
        self.reranker = reranker
        pass
    
    def intention_recognition():
        pass
    def make_noun_interpretation(self,query:str)->List:
        template = self.proper_noun_interpretation().format(query)
        result = self.llm.simple_call_without_history(input=template)
        result_list = json.loads(result)
        return result_list

    def query_aug_main(self,query:str):
        query_for_abs_list = self.make_noun_interpretation(query=query)
        context_list = []
        for i,it in enumerate(query_for_abs_list):
            explanation = self.make_precise_explanation(it)
            context_list.extend(explanation)
        return query_for_abs_list,context_list
    
    def make_precise_explanation(self,query:str):
        context_list = self.make_retrieve_and_rerank(query=query,first_recall=5,last_recall=2)
        context = self.generate_context_num(2,[it['doc'] for it in context_list])
        input = self.precise_explanation_template().format(query,context)
        result = self.llm.simple_call_without_history(input=input)
        return result
    
    def make_retrieve_and_rerank(self,query:str,first_recall:int,last_recall:int):
        list = self.retriever.retrieval_with_paras(query=query,topk=first_recall)
        list = self.reranker.rerank(list,query=query,k=last_recall)
        return list
    # list : [["ids":"","meta":"","doc":""]]

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

    def generate_context_num(self,num:int,text:List):
        context = "" 
        for i,p in enumerate(text):
            context += "Here's the No." + str(i)+" external document:\n"
            context += p + "\n"
        return context
        
    def baseline_template(self):
            template = "You are an accurate and reliable AI assistant able to answer user questions with the help of external documentation, be aware that external documentation may contain noisy factual errors." \
                            "If the information in the document contains the correct answer, you will answer accurately."\
                            "If the information in the document does not contain the answer, you will generate 'There is not enough information in the document, so I cannot answer that question based on the document provided.'" \
                            "If a part of the document contains an error that is not consistent with the facts, please answer 'The document provided has a factual error.'And generate the correct answer." \
                            "Given relevant external documentation, answer user questions based on it." \
                            "Three external documents can be answered in descending order of priority by summarizing their information:" \
                            "Here's the first external documentation:\n---" \
                            "{}\n" \
                            "Here's the second external documentation:" \
                            "{}\n" \
                            "Here's the third external documentation:" \
                            "{}\n" \
                            "user question：\n---" \
                            "{}\n"
            return template
