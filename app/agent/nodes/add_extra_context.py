from datetime import date

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DBInfoState, DateInfoState


async def add_extra_context(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer=runtime.stream_writer
    writer('补充上下文信息')

    query=state['query']


    db_mysql_repository=runtime.context['db_mysql_repository']
    db=await db_mysql_repository.get_db_info()
    db_info=DBInfoState(**db)



    today=date.today()
    date_str=today.strftime('%Y-%m-%d')
    weekday=today.strftime('%A')
    quarter=f'Q{today.month-1//3+1}'
    date_info=DateInfoState(date=date_str,weekday=weekday,quarter=quarter)


    return {'date_info':date_info,'db_info':db_info}