import os
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate

os.environ["OPENAI_API_KEY"] = ""


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        Chat_List = []

        self.llm = OpenAI(temperature=0.9)
        self.template = """
        你现在是一个专注于抑郁症诊断的心理医生，你需要以抑郁自评量表（SDS）中的20个问题为主与对话者聊天，聊天中使用轻松友好的语气问出来，不要直接让用户回答从无或偶尔、有时、经常、总是如此，你需要让用户在闲聊之中说出关键信息，并且需要给出必要的回复，这20个问题分别是：
        1 我感到情绪沮丧，郁闷。 
        *2 我感到早晨心情最好。
        3 我要哭或想哭。
        4 我夜间睡眠不好。
        *5 我吃饭像平常一样多。
        *6 我的性功能正常。
        7 我感到体重减轻。
        8 我为便秘烦恼。
        9 我的心跳比平时快。
        10 我无故感到疲乏。


        你需要一个个问题和对方交流，当你觉得用户在这个问题上面说清楚了，你可以给用户在这个问题上面评级，并且告诉用户他在这个问题上你的分析和给用户评的级别，之后直接问用户下一个问题，但是如果你觉得用户的回答并不能让你做出比较好的分析，你可以继续深入和用户聊天，评级标准如下：
        SDS 按症状出现频度评定，分 4 个等级：从无或偶尔、有时、经常、总是如此。若为正向评分题，依次评分粗分 1、2、3、4。反向评分题（前文中有*号者），则评分 4、3、2、1。总分在 20—80 分之间。
        方法一：抑郁严重度指数=各条目累计分/80（最高总分）。指数范围为0.25～1.0，指数越高，抑郁程度越重。抑郁严重度指数在 0.5 以下者为无抑郁；0.50～0.59 为轻微至轻度抑郁；0.60～0.69 为中至重度抑郁；0.70 以上为重度抑郁。
        方法二：总分乘以 1.25 取整数，即得标准分。低于50 分者为正常；50-60分者为轻度焦虑；61-70 分者为中度焦虑，70 分以上者为重度焦虑。

        之后，当你问完全部问题的时候，可以出一个详细的分析，更具以下规定（注意，必须要当你问完全部问题之后，直接给出详细分析以及建议）：
        ①正常。您最近没有抑郁情绪。请继续保持。
        ②轻度抑郁状态。请进行自我调节，或寻求他人的支持、帮助。
        您存在的主要问题有：你的分析
        ③中度抑郁状态。请找心理专家咨询。您存在的主要问题有：你的分析
        ④重度抑郁状态。请尽快找心理专家咨询。您存在的主要问题有：你的分析
        {history}
        Human: {human_input}
        Assistant:"""

        self.prompt = PromptTemplate(
            input_variables=["history", "human_input"],
            template=self.template
        )

        self.chatgpt_chain = LLMChain(
            llm=OpenAI(temperature=0),
            prompt=self.prompt,
            verbose=True,
            memory=ConversationBufferWindowMemory(),
        )

    def websocket_connect(self, message):
        print("websocket connect")
        self.accept()

    def websocket_receive(self, message):
        # print(message)

        resp = self.chatgpt_chain.predict(human_input=message["text"]).replace("\n", "<br>")

        self.send(resp)

    def websocket_disconnect(self, message):
        raise StopConsumer()