import streamlit as st
import numpy as np
from connector.llm.llm_online import QwenLLM
from core.retriever import Retriever
from core.reranker import Reranker

st.title('🏁 Qwen Import Rag')

client = QwenLLM()
retriver = Retriever()
reranker = Reranker()

# with st.sidebar:
#     if st.button("Home"):
#         st.switch_page("your_app.py")
#     if st.button("Page 1"):
#         st.switch_page("pages/page_1.py")
#     if st.button("Page 2"):
#         st.switch_page("pages/page_2.py")

if "history" not in st.session_state:
    st.session_state.history = []
    
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Say something")
# user_input接收用户的输入
if user_input:
    # 在页面上显示用户的输入
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # get_response_material用来获取模型生成的回复，这个是需要根据自己的情况去实现
    # response为大模型生成的回复，material为RAG的检索的内容
    list = retriver.retrieval(user_input)
    list = reranker.rerank(list,user_input,k=3)
    
    response = client._call(input=user_input,material=list,history=st.session_state.history)
    
    # 将用户的输入加入历史
    st.session_state.history.append({"role": "user", "content": user_input})
    # 在页面上显示模型生成的回复
    with st.chat_message("assistant"):
        st.markdown(str(response))
        tab1, tab2, tab3 = st.tabs([list[0]['ids'],list[1]['ids'],list[2]['ids']])
        with tab1:
            st.header(list[0]['ids'])
            st.markdown(list[0]['doc'])

        with tab2:
            st.header(list[1]['ids'])
            st.markdown(list[1]['doc'])

        with tab3:
            st.header(list[2]['ids'])
            st.markdown(list[2]['doc'])
    # 将模型的输出加入到历史信息中
    st.session_state.history.append({"role": "assistant", "content": response})
    
    # 只保留十轮对话，这个可根据自己的情况设定，我这里主要是会把history给大模型，context有限，轮数不能太多
    if len(st.session_state.history) > 20:
        st.session_state.messages = st.session_state.messages[-20:]

