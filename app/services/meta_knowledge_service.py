import uuid
from dataclasses import asdict
from pathlib import Path

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.models.column_info import ColumnInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.repositories.mysql.db.db_mysql_respositiry import DBMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository


class MetaKnowledgeService:
    def __init__(self, meta_mysql_repository: MetaMysqlRepository,
                       db_mysql_repository: DBMysqlRepository,
                       column_qdrant_repository:ColumnQdrantRepository,
                       embedding_client:HuggingFaceEndpointEmbeddings
                 ):
        self.column_qdrant_repository :ColumnQdrantRepository = column_qdrant_repository
        self.meta_mysql_repository: MetaMysqlRepository = meta_mysql_repository
        self.db_mysql_repository: DBMysqlRepository = db_mysql_repository
        #这里不使用repository层进行数据操作，直接申明客户端即可
        self.embedding_client :HuggingFaceEndpointEmbeddings=embedding_client



    #构建方法
    async def build(self, conf_path: Path):
        # 加载元数据配置文件
        context = OmegaConf.load(conf_path)
        schema = OmegaConf.structured(MetaConfig)

        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

        # logger.info(meta_config.metrics)
        # 同步配置文件的表数据
        if meta_config.tables:
            # 申明更新数据
            table_info_list: list[TableInfo] = []
            column_info_list: list[ColumnInfo] = []

            for table in meta_config.tables:
                # 获取每一张表数据-> meta数据库中table_info表的数据，存入数据库
                table_info= TableInfo(id=table.name,
                                           name=table.name,
                                           role=table.role,
                                           description=table.description
                                           )
                table_info_list.append(table_info)

                columns_dict=await self.db_mysql_repository.select_column_type(table.name)
                # 获取每一表的字段信息-> meta数据库中columns_info表的数据，存入数据库
                for column in table.columns:
                    examples = await self.db_mysql_repository.select_example(column.name,table.name)


                    column_info = ColumnInfo(id=f'{table.name}.{column.name}',
                                                  name=column.name,
                                                  type=columns_dict[column.name],
                                                  role=column.role,
                                                  examples=examples,
                                                  description=column.description,
                                                  alias=column.alias,
                                                  table_id=table.name
                                                  )
                    column_info_list.append(column_info)
            # 插入列表数据，注意事物的管理，使用begin开启事物的自动管理
            async with self.meta_mysql_repository.session.begin():
                self.meta_mysql_repository.insert_table_info(table_info_list)
                self.meta_mysql_repository.insert_column_info(column_info_list)

            # 关闭数据库连接，在外层关闭
            # await self.db_mysql_repository.session.close()
            # await self.meta_mysql_repository.session.close()
            #列信息建立索引,先创建集合
            await self.column_qdrant_repository.ensure_collection()

            #为每一条数据建立索引，为了能尽可能多的命中索引，这里将数据拆分为多个向量（name,description,alias）
            points:list[dict]=[]
            for column_info in column_info_list:
                points.append(
                    {"id":uuid.uuid4(),
                     "vector_text":column_info.name,
                     "payload":asdict(column_info)
                     }
                )
                points.append(
                    {"id":uuid.uuid4(),
                     "vector_text":column_info.description,
                     "payload":asdict(column_info)
                     }
                )

                [ points.append(
                    {"id":uuid.uuid4(),
                     "vector_text": alia,
                     "payload":asdict(column_info)
                     }
                ) for alia in column_info.alias]


            ids=[point.id for point in points]
            vectors=[point["vector_text"] for point in points]
            payloads=[point["payload"] for point in points]

            # 对每个点进行向量化(分批进行)
            vectors=[self.embedding_client.aembed_documents(vectors[i:i+100]) for i in range(0,len(vectors),100)]

            #进行向量存储
            await self.column_qdrant_repository.upsert(ids=ids,vectors=vectors,payloads=payloads)