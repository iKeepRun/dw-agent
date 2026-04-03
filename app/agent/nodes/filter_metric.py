from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, MetricInfoState
from app.utils.load_prompt import load_prompt
from app.core.log import logger

async def filter_metric(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer=runtime.stream_writer
    writer('过滤指标信息')

    query=state['query']
    metric_infos_state: list[MetricInfoState]=state['metric_infos']
    prompt=PromptTemplate(template=load_prompt('filter_metric_info'),input_variables=['query','metric_infos'])

    chain=prompt|llm|JsonOutputParser()

    chain_result=await chain.ainvoke(input={'query':query,'metric_infos':metric_infos_state})

    filter_metric_infos=[metric_info for metric_info in metric_infos_state if metric_info['name'] in chain_result]
    logger.info(f'过滤后的指标信息：{ [filter_metric_info['name'] for filter_metric_info in filter_metric_infos]
}')
    return {'metric_infos':filter_metric_infos}