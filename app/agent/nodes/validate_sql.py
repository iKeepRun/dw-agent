from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def validate_sql(state: DataAgentState,runtime:Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write('验证SQL')

    sql=state['sql']
    db_mysql_repository=runtime.context['db_mysql_repository']

    try:
      await db_mysql_repository.validate_sql(sql)
      return {'error':None}
    except Exception as e:
      logger.info(f'sql发生错误：{str(e)}')
      return {'error':str(e)}
