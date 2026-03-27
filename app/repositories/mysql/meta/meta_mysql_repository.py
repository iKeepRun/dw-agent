from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.mysql_client_manager import meta_mysql_client_manager


class MetaMysqlRepository:
    def __init__(self, session: AsyncSession):
        self.session :AsyncSession = session

    # 这里用同步方法，因为add_all方法是同步方法
    def insert_table_info(self, table_info_list):
        self.session.add_all(table_info_list)

    def insert_column_info(self, column_info_list):
        self.session.add_all(column_info_list)