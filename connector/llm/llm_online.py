from http import HTTPStatus
import os
from pathlib import Path
from typing import Optional,List
from dotenv import load_dotenv
import dashscope
from dashscope import Generation
import random

dashscope.api_key = "sk-dc5d6a75508645be9a03c511a396d909"
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
                        "用户问题：\n---" \
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
        # The response status_code is HTTPStatus.OK indicate success,
        # otherwise indicate request is failed, you can get error code
        # and message from code and message.
        if resp.status_code == HTTPStatus.OK:
            return resp.output.text  # The output text
            # print(resp.usage)  # The usage information
        else:
            # prresp.code)  # The error code.
            return resp.message  # The error message.
    def get_prompt(self, context_1,context_2,context_3, query):

        content = self.prompt_template.format(context_1,context_2,context_3, query)

        return content
    
    def _call(self, input: str,material:List, history:List) -> str:
        messages = history
        prompt = self.get_prompt(material[0],material[1],material[2],input)
        messages.append({'role':'user','content':prompt})
        print(messages)
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
    # env_path = Path('.') / '.env'
    # load_dotenv(dotenv_path=env_path, verbose=True)
    # DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    
    llm = QwenLLM()
    print(llm.sample_sync_call("Hello!"))