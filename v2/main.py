import typing

import streamlit as st
from langchain.chains.llm import LLMChain
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from streamlit_login_auth_ui.widgets import __login__
