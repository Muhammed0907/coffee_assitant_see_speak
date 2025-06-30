import os
from openai import OpenAI


client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPEAPIKEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def PromptUnderstand(msg):
    rule = """
        这个是关于什么，回答一两个字。这个： 
        """
    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model="qwen-plus",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content":  rule + msg},
        ],
        # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
        # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
        # extra_body={"enable_thinking": False},
    )
    # print(completion.choices[0].message.content)
    return completion.choices[0].message.content


# txt = """你是一个友好热情的盲盒推销员。你的主要任务欢迎任何站在你面前的人，为其介绍你所售卖的盲盒，当你正常回复时，使用热情活泼的语气，但保持简短的回答。记住，当你决定回复时，你的目标是让站在你面前的用户愿意使用兑换码段换一个盲盒。每次回复都应该友好且积极，不要使用过于正式的语言"""
# print(PromptUnderstand(txt))