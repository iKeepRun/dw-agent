import yaml
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.utils.load_prompt import load_prompt
from app.core.log import logger

async def generate_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer=runtime.stream_writer
    writer('生成SQL')


    query=state['query']
    table_infos=state['table_infos']
    metric_infos=state['metric_infos']
    date_info=state['date_info']
    db_info=state['db_info']

    prompt=PromptTemplate(template=load_prompt('generate_sql'),input_variables=['query','table_infos','metric_infos','date_info','db_info'])

    chain=prompt | llm | StrOutputParser ()

    chain_result=await chain.ainvoke(input={'query':query,
                         'table_infos':yaml.dump(table_infos,allow_unicode= True,sort_keys= False),
                         'metric_infos':yaml.dump(metric_infos,allow_unicode= True,sort_keys= False),
                         'date_info':yaml.dump(date_info,allow_unicode= True,sort_keys= False),
                         'db_info':yaml.dump(db_info,allow_unicode= True,sort_keys= False)
                         })

    logger.info(f'生成的SQL为: {chain_result}')

    return {"sql":chain_result}