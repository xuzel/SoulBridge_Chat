import typing

import streamlit as st
from langchain.chains.llm import LLMChain
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from streamlit_login_auth_ui.widgets import __login__


# agent class
TOPIC = 0
KEYINFO = 1
DONE = 2


class PhyDoctor:
    def __init__(self, topics: typing.List[typing.List]):
        self.conversation_chain = None
        self.llm = Ollama(model="openchat")
        self.topics = topics
        self.str_output_parser = StrOutputParser()
        self.conversation_abstract = 'None'
        self.user_detail = ''
        self.conversation_history = list()
        self.state = 'choose_topic'
        self.this_topic = list()
        # self.execute('')

    def chat_agent(self, chat_topic: str, chat_key_info: str, user_input: str) -> str:
        def history_conclusion(chat_history: str) -> str:
            # history_conclusion_prompt = """
            # 你是一个聊天历史总结器，你正在进行关于{topic}的聊天，你需要总结这个聊天的内容。聊天历史如下：
            # {history}
            # """
            # history_conclusion_prompt_template = PromptTemplate(
            #     template=history_conclusion_prompt,
            #     input_variables=['topic', 'history']
            # )
            # chain = self.llm | history_conclusion_prompt_template | self.str_output_parser

            prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一个聊天历史总结器，你会受到一个关于{topic}的聊天，你需要总结这个聊天"),
                ("user", "{input}")
            ])
            chain = prompt | self.llm | self.str_output_parser
            output = chain.invoke({
                'topic': chat_topic,
                'input': chat_history
            })
            return output

        chat_prompt_text = """
        你是一个心理咨询专家，和你聊天的患者可能患有精神类疾病，你现在需要通过平缓的语言来于患者交流，以得知其患有什么类型的精神疾病。
        你正在进行一个关于{topic}的对话，在这个对话中，你需要获取用户的关键信息{key_info}，你不能够说的太直白你需要旁敲侧击的询问。
        历史对话总结在此：
        {chat_abstract}
        历史聊天对话:
        {history}
        """
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", chat_prompt_text),
            ("user", "{input}")
        ])

        # chat_prompt_template = PromptTemplate(
        #     input_variables=["history", "human_input", "chat_abstract", "topic", "key_info"],
        #     template=chat_prompt
        # )
        if self.conversation_chain is None:
            self.conversation_chain = chat_prompt | self.llm | self.str_output_parser
            # self.conversation_chain = LLMChain(
            #     llm=self.llm,
            #     prompt=chat_prompt_template,
            #     verbose=True,
            #     memory=ConversationBufferWindowMemory(k=4),
            # )

        llm_output = self.conversation_chain.invoke({
            'input': user_input,
            'topic': chat_topic,
            'key_info': chat_key_info,
            'chat_abstract': self.conversation_abstract,
            'history': str(self.conversation_history)
        })
        print(f"这轮对话的输出:\n{llm_output}")
        self.conversation_history.append({
            'patient': user_input,
            'doctor': llm_output
        })
        self.conversation_abstract = history_conclusion(str(self.conversation_history))
        print(f"当前对话总结:\n{self.conversation_abstract}")
        return llm_output

    def stop_new_conversation(self, user_detail: str) -> bool:
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "你是一个心理医生，你会拿到患者的一些经历以及患者对自己的看法等，你需要判断你获得的东西能否判断用户是否患有精神类疾病，如果患有你返回true，不患有，返回false，除了这两个你不需要返回任何东西"),
            ("user", "{input}")
        ])
        chain = prompt | self.llm | self.str_output_parser
        output = chain.invoke({
            'input': user_detail
        })
        print(f"是否进行新的对话:{output}")
        return True if 'true' in output else False

    def topic_scheduling(self):
        for index, topic in enumerate(self.topics):
            if topic[DONE]:
                continue
            self.topics[index][DONE] = True
            print(f"接下来的话题:\n{topic}")
            return topic

    def add_conclusion(self):
        conclusion_prompt_text = """
        你是心理咨询总结器，你会得到一个患者已经有的信息以及患者之前于医生的聊天历史，你需要判断聊天历史中有用的信息并且将这些信息整合到已经有的患者信息中。
        患者已经有的信息如下：
        {user_info}

        医生以及患者新的聊天记录如下：
        {conversation}
        """
        conclusion_prompt = PromptTemplate(
            input_variables=["user_info", "conversation"],
            template=conclusion_prompt_text
        )

        add_conclusion_chain = LLMChain(
            llm=self.llm,
            prompt=conclusion_prompt,
            verbose=True,
        )
        output = add_conclusion_chain.predict(user_info=self.user_detail, conversation=self.conversation_history)
        print(f"更新用户信息如下:\n{self.conversation_abstract}")
        return output

    def report_generate(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "你是一个心理医生，你会拿到关于患者的一些信息，你需要判断患者是否患有精神类疾病，并详细说出判断原因并给出报告，输出使用markdown格式"),
            ("user", "{input}")
        ])
        chain = prompt | self.llm | self.str_output_parser
        output = chain.invoke({
            'input': self.user_detail
        })
        print(f"生成的报告如下:\n{output}")
        return output

    def stop_chat(self, chat_topic, key_info):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "你是一个心理医生，你正在和患者进行主题为{topic}的聊天，你会得到一个聊天记录，你需要判断这个聊天记录是否获取的关键信息{key}，如果获取了并且可以停止聊天了，你需要返回Ture，否则返回False，注意，除了这两个之外你不能返回其他值"),
            ("user", "{input}")
        ])
        chain = prompt | self.llm | self.str_output_parser
        output = chain.invoke({
            'input': str(self.conversation_history),
            'topic': chat_topic,
            'key': key_info
        })
        print(f"当前聊天是否获取了足够的信息:\n{output}")
        if 'true' in output:
            self.conversation_history = str()
            self.conversation_abstract = str()
            self.conversation_chain = None
        return True if 'True' in output else False

    def execute(self, user_input):
        if not self.this_topic:
            self.this_topic = self.topic_scheduling()
            self.state = 'chat'
            with st.chat_message("assistant"):
                st.markdown(f"我们接下来开始关于{self.this_topic[TOPIC]}的对话吧。")
            st.session_state.messages.append(
                {"role": "assistant", "content": f"我们接下来开始关于{self.this_topic[TOPIC]}的对话吧。"})
            return

        else:
            llm_replay = self.chat_agent(self.this_topic[TOPIC], self.this_topic[KEYINFO], user_input)
            with st.chat_message("assistant"):
                st.markdown(llm_replay)
            st.session_state.messages.append({"role": "assistant", "content": llm_replay})
            if self.stop_chat(self.this_topic[TOPIC], self.this_topic[KEYINFO]):
                if self.stop_new_conversation(self.user_detail):
                    st.session_state.messages.append({"role": "assistant", "content": self.report_generate()})
                    return
                else:
                    self.this_topic = self.topic_scheduling()
                    if self.this_topic is None:
                        pass
                    with st.chat_message("assistant"):
                        st.markdown(f"我们接下来开始关于{self.this_topic[TOPIC]}的对话吧。")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"我们接下来开始关于{self.this_topic[TOPIC]}的对话吧。"})

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
