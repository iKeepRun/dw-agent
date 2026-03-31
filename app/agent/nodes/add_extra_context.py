from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


def add_extra_context(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    print('添加额外上下文')