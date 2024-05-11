import streamlit as st
import numpy as np
from connector.llm.llm_online import QwenLLM
from core.retriever import Retriever
from core.reranker import Reranker
from utils.onlineloader.pdfLoader import pdfLoader

st.title('🏁 Qwen Import Rag')

client = QwenLLM()
retriver = Retriever()
reranker = Reranker()
online = pdfLoader(retriver.db,retriver.emb_model)

class OneMsg:
    role:str
    text:str
    context:object = None # [{ids:"",title:"",authors:"",content:"",child:[{}]]
    
    def __init__(self,role,text,context):
        self.role = role
        self.text = text
        self.context = context

if "history" not in st.session_state:
    st.session_state.history = list(OneMsg)

if "history_for_UI" not in st.session_state:
    st.session_state.history_for_UI = list(OneMsg)

# 历史渲染
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])
        if message["context"].count > 0 :
            # TABS
            with st.expander("See RAG Info"):
                with st.tabs(piece["ids"]): #
                    for id,piece in message["context"]:
                        # st.tabs(it["ids"]) 需要这样吗？
                        with st.expander("See RAG Info"):
                            st.markdown(message["context"][id]["title"])
                            st.markdown(message["context"][id]["authors"])
                            st.markdown(message["context"][id]["content"])
                            # 子TABS 
                            if message["context"][id]["child"].count > 0 :
                                with st.expander("See RAG Info"):
                                    for index,small_piece in enumerate(message["context"][id]["child"]):
                                        # st.tabs(it["ids"]) 需要这样吗？
                                        with st.tabs(str(index)):
                                            st.markdown(small_piece["content"])

    

user_input = st.chat_input("Say something")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    # 将用户的输入加入历史
    user_piece = OneMsg("user",user_input,[])
    st.session_state.history.append(user_piece)
    # I want to know something about RAG ! 
    
    list = retriver.retrieval(user_input)
    list = reranker.rerank(list,user_input,k=3)
    print(list)
    
    in_temp = []
    for it in list:
        online.load_pdf_doc(it['ids'])
        temp_list = retriver.retrieval_in_temp(user_input)
        temp_list = reranker.rerank(temp_list,user_input,k=2)
        in_temp.append(temp_list)
    
    
    response = client.in_temp_call(input=user_input,material=in_temp,history=st.session_state.history)
    
    # 将模型的输出加入到历史信息中
    st.session_state.history.append({"role": "assistant", "content": response})
    
    # 只保留十轮对话，这个可根据自己的情况设定，我这里主要是会把history给大模型，context有限，轮数不能太多
    if len(st.session_state.history) > 20:
        st.session_state.messages = st.session_state.messages[-20:]

