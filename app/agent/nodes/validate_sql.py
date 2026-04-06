from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def validate_sql(state: DataAgentState,runtime:Runtime[DataAgentContext]):
    write = runtime.stream_writer
    # write('验证SQL')
    write({'type':'progress','step':'验证SQL','status':'running'})

    try :
        sql=state['sql']
        db_mysql_repository=runtime.context['db_mysql_repository']

        try:
          await db_mysql_repository.validate_sql(sql)
          write({'type': 'progress', 'step': '验证SQL', 'status': 'success'})
          return {'error':None}
        except Exception as e:
          logger.info(f'sql发生错误：{str(e)}')
          write({'type': 'progress', 'step': '验证SQL', 'status': 'success'})
          return {'error':str(e)}
    except Exception as e:
        logger.error(f'验证SQL失败: {e}')
        write({'type':'progress','step':'验证SQL','status':'error'})
        raise e