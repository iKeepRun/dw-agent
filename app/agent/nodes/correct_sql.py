from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState

def correct_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    print('校正sql')