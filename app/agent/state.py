from typing_extensions import TypedDict

from app.entities.column_info import ColumnInfo
from app.entities.value_info import ValueInfo


class DataAgentState(TypedDict):
    query:str  #用户输入查询信息
    error:str  #校验sql错误信息
    keywords:list[str] #分词列表
    retrieved_column_infos:list[ColumnInfo]  #召回的字段信息(去重)
    value_infos:list[ValueInfo]  #召回的字段信息(去重)