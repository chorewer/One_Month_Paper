from typing import Optionial,List
from dashscope import Generation
import random

load_dotenv(verbose=True)

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
        
    def _call(self, prompt: str, history: List[List[str]]) -> str:
        messages = []
        for pair in history:
            question, answer = pair
            messages.append({"role": "user", "text": question})
            messages.append({"role": "assistant", "text": answer})
        messages.append({"role": "user", "text": prompt})
        print(messages)
        try:
            response = Generation.call(
                model=self.model,
                messages=messages,
                # 设置随机数种子seed，如果没有设置，则随机数种子默认为1234
                seed=random.randint(1, 10000),
                # 将输出设置为"message"格式
                result_format='message'
            )
            if response.status_code == HTTPStatus.OK:
                print(response)
                return response.output.choices[0].message if response.output.choices[0] else {}
            else:
                print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                    response.request_id, response.status_code,
                    response.code, response.message
                ))
                return {}
        except Exception as e:
            print(f"Error calling Qwen API: {e}")
            return ""