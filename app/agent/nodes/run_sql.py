from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger
async def run_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write('执行SQL')

    sql = state['sql']
    db_mysql_repository = runtime.context['db_mysql_repository']


    result= await db_mysql_repository.run( sql)
    logger.info(f'SQL执行结果为: {result}')