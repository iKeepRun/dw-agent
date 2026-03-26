from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.mysql_client_manager import meta_mysql_client_manager


class MetaMysqlRepository:
    def __init__(self, session: AsyncSession):
        self.session :AsyncSession = session