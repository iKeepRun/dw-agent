from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.entities.value_info import ValueInfo
from app.utils.load_prompt import load_prompt
from app.core.log import logger

async def recall_value(state:DataAgentState,runtime:Runtime[DataAgentContext]):
   write = runtime.stream_writer
   write({'type':'progress','step':'召回字段取值','status':'running'})

   try:
       query = state['query']
       keywords = state['keywords']
       value_es_repository=runtime.context['value_es_repository']

       # 使用大模型扩展检索值
       prompt=PromptTemplate(template=load_prompt("extend_keywords_for_value_recall"),input_variables=[query])
       extend_value_chain= prompt | llm | JsonOutputParser()

       extend_query=await extend_value_chain.ainvoke({"query":query})

       results=set(keywords+extend_query)
       logger.info(f'召回值节点-->最终的提取关键词为: {results}')
       value_infos_map:dict[str,ValueInfo]={}
       for result in results:
           value_infos_list:list[ValueInfo]=await  value_es_repository.select(result)

           for value_info in value_infos_list:
               if value_info.id  not in value_infos_map:
                   value_infos_map[value_info.id]=value_info
       logger.info(f'召回的取值信息为：{value_infos_map.keys()}')

       write({'type':'progress','step':'召回字段取值','status':'success'})

       return   {"value_infos":list(value_infos_map.values())}
   except Exception as e:
       logger.error(f'召回字段取值失败: {e}')
       write({'type':'progress','step':'召回字段取值','status':'error'})
       raise e