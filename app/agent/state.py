from typing_extensions import TypedDict


class DataAgentState(TypedDict):
    query:str  #用户输入查询信息
    error:str  #校验sql错误信息
    keywords:list[str] #分词列表