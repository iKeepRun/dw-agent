from marshal import load

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.runtime import Runtime
from win32trace import write

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.utils.load_prompt import load_prompt


def recall_column(state:DataAgentState,runtime:Runtime[DataAgentContext]):

    write=runtime.stream_writer
    write('召回字段信息')

    column_qdrant_repository=runtime.context['column_qdrant_repository']
    # 获取关键词
    keywords=state['keywords']

    prompt=ChatPromptTemplate.from_template(load_prompt('extend_keywords_for_column_recall'))
    # 大模型补充关键词
    extra_keywords= prompt | llm | JsonOutputParser()

