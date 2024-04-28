import typing

import streamlit as st
from langchain.chains.llm import LLMChain
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from streamlit_login_auth_ui.widgets import __login__


# agent class


# log in

# main page

def main_page():
    # 设置页面布局
    # st.set_page_config(layout="wide")

    # Initialize chat history

    # 在侧边栏添加选择器和按钮
    with st.sidebar:
        st.title("聊天配置")
        # 模型选择pass
        model_choice = st.selectbox("选择模型", ["openchat(推荐)", "llama2-7B", "chatgpt4", "chatgpt-3.5"])

        submit_button = st.button("应用配置")
        clear_history = st.button("清空历史")
        if clear_history or submit_button:
            st.session_state.messages = []
        # 初始化或获取 session_state 中的信息
        if 'num_inputs' not in st.session_state:
            st.session_state.num_inputs = 1  # 输入框的初始数量
        if 'inputs' not in st.session_state:
            st.session_state.inputs = []  # 存储输入值的列表

        # 在侧边栏添加一个按钮，用于增加输入框
        if st.sidebar.button('增加话题-目标'):
            st.session_state.num_inputs += 1  # 增加输入框数量

        # 根据需要的输入框数量创建输入框
        input_values = []
        for i in range(st.session_state.num_inputs):
            new_topic = st.text_input(f"topic {i + 1}", key=f"topic_{i}")
            new_key_info = st.text_input(f"key info {i + 1}", key=f"info_{i}")
            input_values.append([new_topic, new_key_info])  # 将当前输入框的内容添加到列表

        # 更新 session_state 中的 inputs 列表
        st.session_state.inputs = input_values
        print(st.session_state.inputs)

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if user_input := st.chat_input("What is up?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(user_input)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # response = conversation_with_summary.predict(input=user_input)
        st.session_state.my_obj.execute(user_input)
        # Display assistant response in chat message container

        # with st.chat_message("assistant"):
        #     st.markdown(response)
        # # # Add assistant response to chat history
        # st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == '__main__':
    login()
