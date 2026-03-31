from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


def extract_keywords(state: DataAgentState, runtime:Runtime[DataAgentContext]):
    print('抽取关键词')
    # return {'msg': 'extract_keywords'}