from http import HTTPStatus
import os
from pathlib import Path
from typing import Optional,List
from dotenv import load_dotenv
import dashscope
from dashscope import Generation
import random

load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

def build_template():
        prompt_template = "You are an accurate and reliable AI assistant able to answer user questions with the help of external documentation, be aware that external documentation may contain noisy factual errors." \
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
        return prompt_template
    
class QwenLLM:
    model : str = "qwen-turbo"
    token_window : int = 4096
    max_token: int = 512
    offcut_token: int = 50
    truncate_len: int = 50
    temperature: float = 0
    
    history: List[List[str]] = []
    history_len: int = 2
    
    def __init__(self):
        self.model = "qwen-turbo"
        self.prompt_template = build_template()
    
    def sample_sync_call(self,text : str):
        prompt_text = text
        resp = dashscope.Generation.call(
            model='qwen-turbo',
            prompt=prompt_text
        )
        if resp.status_code == HTTPStatus.OK:
            return resp.output.text  # The output text
            # print(resp.usage)  # The usage information
        else:
            # prresp.code)  # The error code.
            return resp.message  # The error message.
    def get_prompt(self, context_1,context_2,context_3, query):

        content = self.prompt_template.format(context_1,context_2,context_3, query)

        return content
    def simple_call_without_history(self,sys_msg:str = "You are a helpful assitant.",input:str="") -> str:
        messages = [{'role': 'system', 'content': sys_msg},
                {'role': 'user', 'content': input}]
        response = Generation.call(model="qwen-turbo",
                                messages=messages,
                                # 将输出设置为"message"格式
                                result_format='message')
        if response.status_code == HTTPStatus.OK:
            # print(response)
            return response['output'].choices[0].message['content']
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            return response.message
        
    def simple_call(self,sys_msg:str = "You are a helpful assitant.",input:str = "",history:List = []) -> str:
        messages = [{'role': 'system', 'content': sys_msg}]
        if history.count > 0:
            messages = history
        messages.append({'role': 'user', 'content': input})
        response = Generation.call(model="qwen-turbo",
                                messages=messages,
                                # 将输出设置为"message"格式
                                result_format='message')
        if response.status_code == HTTPStatus.OK:
            # print(response)
            return response['output'].choices[0].message['content']
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            return response.message
    
    def _call(self, input: str,material:List, history:List) -> str:
        messages = history
        prompt = self.get_prompt(material[0],material[1],material[2],input)
        messages.append({'role':'user','content':prompt})
        # print(messages)
        response = Generation.call(model="qwen-turbo",
                                messages=messages,
                                # 将输出设置为"message"格式
                                result_format='message')
        if response.status_code == HTTPStatus.OK:
            # print(response)
            return response['output'].choices[0].message['content']
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            return response.message
        
    def in_temp_call(self, input: str,material:List, history:List) -> str:
        messages = history
        prompt = self.get_prompt(material[0][0]['doc']+material[0][1]['doc'],
                                 material[1][0]['doc']+material[1][1]['doc'],
                                 material[2][0]['doc']+material[2][1]['doc'],input)
        messages.append({'role':'user','content':prompt})
        # print(messages)
        response = Generation.call(model="qwen-turbo",
                                messages=messages,
                                # 将输出设置为"message"格式
                                result_format='message')
        if response.status_code == HTTPStatus.OK:
            # print(response)
            return response['output'].choices[0].message['content']
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            return response.message



        
if __name__ == "__main__":
    llm = QwenLLM()
    print(llm.sample_sync_call("Hello!"))