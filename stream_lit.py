import random
from typing import List
import streamlit as st
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()
os_home_directory = os.getenv("HOME_DIRECTORY")
import sys
sys.path.append(os_home_directory)
from pattern import return_pattern
from utils.OneMsg import OneMsg

st.title('🏁 Qwen Import Rag')



if "history" not in st.session_state:
    st.session_state.history = []

if "history_for_UI" not in st.session_state:
    st.session_state.history_for_UI = []

if "pdf_downloaded" not in st.session_state:
    st.session_state.pdf_downloaded = []
    
if "src_list_doc" not in st.session_state:
    st.session_state.src_list_doc = []

if "id_list" not in st.session_state:
    st.session_state.id_list = 0

def downloading(piece):
    # global pattern
    return_pattern().document_in_pdf(piece["ids"]) # 装载文档 
    st.text("Successful download")
    piece["pdf"] = True
    st.session_state.pdf_downloaded.append(piece["ids"])
    temp_obj = {
        "ids" : piece["ids"],
        "title" : piece["title"],
        "authors" : piece["authors"],
        "content" : piece["content"]
    }
    st.session_state.src_list_doc.append(temp_obj)
def subtab_print(index,small_piece):
    with st.expander("See More Info"):
        st.markdown(small_piece["content"])

def tab_print(id,piece,level):
    but_disabled = False
    if bool(piece["pdf"]) == True:
        but_disabled=True
    keys = piece["ids"]+str(level)
    # st.session_state.id_list += 1
    # print(keys)
    with st.expander("See RAG Info"):
        st.markdown("#### "+piece["title"])
        st.markdown("*"+piece["authors"]+"*")
        st.markdown(piece["content"])
        if piece["ids"] in st.session_state.pdf_downloaded : 
            piece["pdf"] = True
        if st.button("Download",key=keys,disabled=but_disabled):
            print("on_click")
            return_pattern().document_in_pdf(piece["ids"]) # 装载文档 
            st.text("Successful download")
            piece["pdf"] = True
            st.session_state.pdf_downloaded.append(piece["ids"])
            temp_obj = {
                "ids" : piece["ids"],
                "title" : piece["title"],
                "authors" : piece["authors"],
                "content" : piece["content"]
            }
            st.session_state.src_list_doc.append(temp_obj)
        # 子TABS 
        if len(piece["child"]) > 0 :
            with st.expander("See RAG Info"):
                sub_tabs = st.tabs([str(v) for v,it in enumerate(piece["child"])])
                for index,small_piece in enumerate(piece["child"]):
                    with sub_tabs[index]:
                        # st.tabs(it["ids"]) 需要这样吗？
                        subtab_print(index,small_piece)

def print_one_Msg(level,message):
    with st.chat_message(message.role):
            st.markdown(message.text)
            if len(message.context) > 0 :
                # TABS
                tabs = st.tabs([it["ids"] for it in message.context])
                for id,piece in enumerate(message.context):
                    with tabs[id]: #
                        # print(piece['ids'])
                        # with st.expander("See RAG Info"):
                        tab_print(id,piece,level)
def print_all_history():
    for level,message in enumerate(st.session_state.history):
        print_one_Msg(level,message)
    
def msglist2responselist(list):
    result = []
    for k,it in enumerate(list):
        ids = "Paper ids " + it['ids'] + " \n"
        title = "Paper title " + it['title'] + " \n"
        author = "Author : " + it["authors"] + " \n"
        content = it["content"] + "\n"
        childs = ""
        for t in it["child"]:
            childs += t + "\n"
        result.append({"doc":ids + title + author + content + childs})
    return result

def fill_context_list(list_inner,context_list_for_OneMsg,list):
    for it in list_inner:
        # 寻找具有属性 ats 为 2 的对象
        found = False
        for obj in context_list_for_OneMsg:
            if obj["ids"] == it["meta"]["from"]:
                found = True
                obj["child"].append(it["doc"])
                break
        # 如果没有找到，创建新的对象并添加到列表中
        if not found:
            match_doc = st.session_state.pdf_downloaded.index(it["meta"]["from"])
            match_doc = st.session_state.src_list_doc[match_doc]
            i_child = []
            i_child.append(it["doc"])
            context_list_for_OneMsg.append({
                "ids": match_doc["ids"],
                "title": match_doc["title"],
                "authors": match_doc["authors"],
                "pdf" : True,
                "content": match_doc["content"],
                "child": i_child
            })
        
    for it in list:
        # print(it)
        found = False
        for obj in context_list_for_OneMsg:
            if obj["ids"] == it["ids"]:
                found = True
                break
        if not found:    
            context_list_for_OneMsg.append({
                "ids": it["ids"],
                "title": it["meta"]["title"],
                "authors": it["meta"]["author"],
                "pdf" : False,
                "content": it["doc"],
                "child": []
            })
# 历史渲染
print_all_history()
    

user_input = st.chat_input("Say something")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    # 将用户的输入加入历史 并渲染
    user_piece = OneMsg("user",user_input,[])
    
    print_one_Msg(len(st.session_state.history),user_piece)
    # I want to know something about RAG ! 
    result = return_pattern().intention_recognition(user_input,history = st.session_state.history)
    print("IF RAG ? : "+result)
    # 是否使用 RAG  搜索
    rag = True
    if "No" in result:
        rag = False
    
    context_list_for_OneMsg = []
    list_for_response = []
    list_inner = return_pattern().inner_search(query=user_input)
    list = []
    if rag:
        list = return_pattern().make_retrieve_and_rerank(query=user_input,first_recall=7,last_recall=5)
    fill_context_list(list_inner,context_list_for_OneMsg,list)
    list_for_response = msglist2responselist(context_list_for_OneMsg)
    print(list_for_response)
    result,remove = return_pattern().make_response_history(query=user_input,data=list_for_response,history = st.session_state.history,rag=True)
    # print(result)
    # print(remove)
    # if rag:
    for it in reversed(remove):
        if len(context_list_for_OneMsg) > 0:
            context_list_for_OneMsg.pop(it)
    # the paper A Mechanistic Understanding of Alignment Algorithms:A Case Study on DPO and Toxicity
    # what kind of LLM do they use to do the experience .
    
    model_piece = OneMsg("assistant",result,context_list_for_OneMsg)
    print_one_Msg(len(st.session_state.history)+1,model_piece)
    # 将模型的输出加入到历史信息中
    st.session_state.history.append(user_piece)
    st.session_state.history.append(model_piece)
    
    # 只保留十轮对话，这个可根据自己的情况设定，我这里主要是会把history给大模型，context有限，轮数不能太多
    if len(st.session_state.history) > 20:
        st.session_state.messages = st.session_state.messages[-20:]

