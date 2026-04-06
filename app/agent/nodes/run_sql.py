from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def run_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write({'type':'progress','step':'执行SQL','status':'running'})

    try:
        sql = state['sql']
        db_mysql_repository = runtime.context['db_mysql_repository']

        result= await db_mysql_repository.run( sql)
        logger.info(f'SQL执行结果为: {result}')

        write({'type':'progress','step':'执行SQL','status':'success'})
        write({'type':'result', 'data': result})
        # return {'result': result}
    except Exception as e:
        logger.error(f'执行SQL失败: {e}')
        write({'type':'progress','step':'执行SQL','status':'error'})
        raise e