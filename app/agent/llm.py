import os

from langchain.chat_models import init_chat_model

llm=init_chat_model(
    model_provider='openai',
    model='qwen-plus',
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0,
)

if __name__ == '__main__':
   res=llm.invoke("你好")
   print(res.content)