import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, TableInfoState
from app.utils.load_prompt import load_prompt
from app.core.log import logger


async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer('过滤表')

    table_infos_state = state['table_infos']
    query = state['query']
    prompt = PromptTemplate(template=load_prompt('filter_table_info'), input_variables=['query', 'table_infos'])

    chain = prompt | llm | JsonOutputParser()
    result = await chain.ainvoke(
        input={'query': query, 'table_infos': yaml.dump(data=table_infos_state, allow_unicode=True, sort_keys=False)})

    logger.info(f'大模型输出结果：{result}')

    # 根据大模型返回的表名和字段名过滤表信息
    filter_table_infos: list[TableInfoState] = []

    for table_info in table_infos_state:
        table_name = table_info['name']

        # 检查该表是否在大模型返回的结果中
        if table_name in result:
            # 获取该表中需要保留的字段列表
            required_columns = result[table_name]

            # 过滤出需要的字段
            filtered_columns = [
                col for col in table_info['columns']
                if col['name'] in required_columns
            ]

            # 如果有需要保留的字段，则创建新的表信息
            if filtered_columns:
                filtered_table: TableInfoState = {
                    'name': table_name,
                    'role': table_info['role'],
                    'description': table_info['description'],
                    'columns': filtered_columns
                }
                filter_table_infos.append(filtered_table)
    # logger.info(f'过滤后的表信息：{[filter_table_info['name'] for filter_table_info in filter_table_infos]}')
    logger.info(f'过滤后的表信息：{filter_table_infos}')

    return {'table_infos': filter_table_infos}
