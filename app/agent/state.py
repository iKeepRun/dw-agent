from typing_extensions import TypedDict

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo


class ColumnInfoState(TypedDict):
    name: str
    type: str
    role: str
    examples: list
    description: str
    alias: list[str]

class TableInfoState(TypedDict):
    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]
    
class MetricInfoState(TypedDict):
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]

class DataAgentState(TypedDict):
    query:str  #用户输入查询信息
    error:str  #校验sql错误信息
    keywords:list[str] #分词列表
    retrieved_column_infos:list[ColumnInfo]  #召回的字段信息(去重)
    retrieved_metric_infos:list[MetricInfo]  #召回的指标信息(去重)
    value_infos:list[ValueInfo]              #召回的值信息(去重)

    table_infos: list[TableInfoState]   # 表信息
    metric_infos: list[MetricInfoState]   # 指标信息