from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState

def merge_retrieved_info(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    print('合并信息')