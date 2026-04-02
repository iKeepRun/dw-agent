from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, ColumnInfoState, TableInfoState, MetricInfoState
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.models.column_info import ColumnInfoMySQL


async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer('合并信息')

    # 节点需要用的依赖
    retrieved_metric_infos = state['retrieved_metric_infos']
    retrieved_column_infos = state['retrieved_column_infos']
    value_infos = state['value_infos']

    meta_mysql_repository=runtime.context['meta_mysql_repository']

    column_infos_map:dict[str,ColumnInfo]= {retrieved_column_info.id: retrieved_column_info for retrieved_column_info in retrieved_column_infos}
    # 构建表数据
      # 指标关联字段补充到column_info中(去重)
    for metric_info in retrieved_metric_infos:
        for relevant_column in metric_info.relevant_columns:
             if relevant_column not in column_infos_map:
                # async with meta_mysql_repository.session.begin():  查询操作不需要提交事务
                   column_info=await meta_mysql_repository.get_column_info_by_id(relevant_column)
                   column_infos_map[relevant_column]=column_info


      # 将字段取值添加到column_info的examples中
    for value_info in value_infos:
        column_id=value_info.column_id
        value=value_info.value
        if column_id not in column_infos_map:
            column_info=await meta_mysql_repository.get_column_info_by_id(column_id)
            column_infos_map[column_id]=column_info
        if value not in column_infos_map[column_id].examples:
            column_infos_map[column_id].examples.append(value)

      # 构建需要的目标数据table_infos
    table_to_column_map:dict[str,list[ColumnInfo]]={}
       # 根据table_id进行分组
    for column_info in column_infos_map.values():
       table_id=column_info.table_id
       if table_id not in table_to_column_map:
           table_to_column_map[column_info.table_id]=[]
       table_to_column_map[table_id].append(column_info)

      # 强制添加表的主外键字段（避免大模型召回的不稳定性）
    for key in table_to_column_map.keys():
        key_columns:list[ColumnInfo]=await  meta_mysql_repository.get_key_info_by_id(key)
        column_ids=[ column_info.id for column_info in table_to_column_map[key]]
        for key_column in key_columns:
            if key_column.id not in column_ids:
                table_to_column_map[key].append(key_column)

      # 将表信息整理成目标格式
    table_infos:list[TableInfoState]=[]
    for table_id, column_infos in table_to_column_map.items():
        table_info:TableInfo=await meta_mysql_repository.get_table_info_by_id(table_id)
        columns=[ColumnInfoState(
            name=column_info.name,
            type=column_info.type,
            role=column_info.role,
            examples=column_info.examples,
            description=column_info.description,
            alias=column_info.alias,
        )for column_info in column_infos]

        table_info_state:TableInfoState=TableInfoState(
             name=table_info.name,
             role=table_info.role,
             description=table_info.description,
             columns=columns,
        )

        table_infos.append(table_info_state)
    # 构建指标数据
    metric_infos:list[MetricInfoState]=[MetricInfoState(
        name=retrieved_metric_info.name,
        description=retrieved_metric_info.description,
        relevant_columns=retrieved_metric_info.relevant_columns,
        alias=retrieved_metric_info.alias,
    ) for retrieved_metric_info in retrieved_metric_infos]


    return {
        'table_infos':table_infos,
        'metric_infos':metric_infos,
    }