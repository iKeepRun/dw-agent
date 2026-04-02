from marshal import load

from dns.e164 import query
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langgraph.runtime import Runtime
from win32trace import write

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.utils.load_prompt import load_prompt
from app.core.log import logger


async def recall_column(state:DataAgentState,runtime:Runtime[DataAgentContext]):

    write=runtime.stream_writer
    write('召回字段信息')

    column_qdrant_repository=runtime.context['column_qdrant_repository']
    embedding_client=runtime.context['embedding_client']
    # 获取关键词
    keywords=state['keywords']
    # logger.info(f'字段召回接收到的关键词为: {keywords}')
    query=state['query']
    prompt=PromptTemplate(template=load_prompt('extend_keywords_for_column_recall'), input_variables=['query'])
    # prompt=ChatPromptTemplate.from_template(load_prompt('extend_keywords_for_column_recall'))
    # 大模型补充关键词
    extra_keywords_chain= prompt | llm | JsonOutputParser()

    extra_keywords=await  extra_keywords_chain.ainvoke(input={'query':query})

    # logger.info(f'大模型补充的关键词为: {extra_keywords}')
    final_keywords=list(set(keywords+extra_keywords))
    logger.info(f'召回字段节点-->最终的提取关键词为: {final_keywords}')
    # 批量向量化
    embedding_steps=4
    embedding_texts:list[list[float]]=[]
    for i in range(0,len(final_keywords),embedding_steps):
        embedding_currents=await embedding_client.aembed_documents(final_keywords[i:i+embedding_steps])
        embedding_texts.extend(embedding_currents)


    retrieved_column_infos=await column_qdrant_repository.query_points(embedding_texts)

    ids=[retrieved_column_info.id for retrieved_column_info in retrieved_column_infos]
    logger.info(f'召回的字段信息为: {ids}')
    return {"retrieved_column_infos":retrieved_column_infos}
# if __name__ == '__main__':
    # res=load_prompt('extend_keywords_for_column_recall')
    # print(res)
