from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


def validate_sql(state: DataAgentState,runtime:Runtime[DataAgentContext]):
    print('验证SQL')
    return {'error':None}