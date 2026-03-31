from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


def filter_table(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    print('过滤表信息')