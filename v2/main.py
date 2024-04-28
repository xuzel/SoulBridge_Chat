import typing

import streamlit as st
from langchain.chains.llm import LLMChain
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from streamlit_login_auth_ui.widgets import __login__


# agent class


# log in
st.title("Soul-Bridge")
if "messages" not in st.session_state:
    st.session_state.messages = []

topic_list = [
    ['情绪波动', '情绪变化的频率与强度以及原因', False],
    ['睡眠质量', '睡眠模式(如难以入睡、频繁醒来)', False],
    ['社交活动', '社交活动的频率与类型', False],
    ['思维模式', '全有或全无的思维', False],

]
if 'my_obj' not in st.session_state:
    st.session_state.my_obj = PhyDoctor(topic_list)
# doctor = PhyDoctor(topic_list)


def login():
    __login__obj = __login__(auth_token="courier_auth_token",
                             company_name="Shims",
                             width=200, height=250,
                             logout_button_name='Logout', hide_menu_bool=False,
                             hide_footer_bool=False,
                             lottie_url='https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

    LOGGED_IN = __login__obj.build_login_ui()

    if LOGGED_IN:
        main_page()


# main page