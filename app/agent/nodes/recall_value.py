from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


def recall_value(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    print('召回字段取值')