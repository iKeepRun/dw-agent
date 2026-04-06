from datetime import date

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DBInfoState, DateInfoState
from app.core.log import logger


async def add_extra_context(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer=runtime.stream_writer
    writer({'type':'progress','step':'补充上下文信息','status':'running'})

    try:
        query=state['query']


        db_mysql_repository=runtime.context['db_mysql_repository']
        db=await db_mysql_repository.get_db_info()
        db_info=DBInfoState(**db)



        today=date.today()
        date_str=today.strftime('%Y-%m-%d')
        weekday=today.strftime('%A')
        quarter=f'Q{today.month-1//3+1}'
        date_info=DateInfoState(date=date_str,weekday=weekday,quarter=quarter)

        writer({'type':'progress','step':'补充上下文信息','status':'success'})

        return {'date_info':date_info,'db_info':db_info}
    except Exception as e:
        logger.error(f'补充上下文信息失败: {e}')
        writer({'type':'progress','step':'补充上下文信息','status':'error'})
        raise e