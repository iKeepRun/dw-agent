import uuid
from dataclasses import asdict
from pathlib import Path

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.entities.column_info import ColumnInfo
from app.entities.column_metric import ColumnMetric
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.models.column_info import ColumnInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.db.db_mysql_respositiry import DBMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository


class MetaKnowledgeService:
    def __init__(self, meta_mysql_repository: MetaMysqlRepository,
                 db_mysql_repository: DBMysqlRepository,
                 column_qdrant_repository: ColumnQdrantRepository,
                 embedding_client: HuggingFaceEndpointEmbeddings,
                 value_es_repository: ValueEsRepository
                 ):
        self.column_qdrant_repository: ColumnQdrantRepository = column_qdrant_repository
        self.meta_mysql_repository: MetaMysqlRepository = meta_mysql_repository
        self.db_mysql_repository: DBMysqlRepository = db_mysql_repository
        # 这里不使用repository层进行数据操作，直接申明客户端即可
        self.embedding_client: HuggingFaceEndpointEmbeddings = embedding_client
        # es数据层对象
        self.value_es_repository = value_es_repository

    async def _save_tables_to_meta_db(self, meta_config: MetaConfig) -> list[ColumnInfo]:
        # 申明更新数据
        table_info_list: list[TableInfo] = []
        column_info_list: list[ColumnInfo] = []

        for table in meta_config.tables:
            # 获取每一张表数据-> meta数据库中table_info表的数据，存入数据库
            table_info = TableInfo(id=table.name,
                                   name=table.name,
                                   role=table.role,
                                   description=table.description
                                   )
            table_info_list.append(table_info)

            columns_dict = await self.db_mysql_repository.select_column_type(table.name)
            # 获取每一表的字段信息-> meta数据库中columns_info表的数据，存入数据库
            for column in table.columns:
                examples = await self.db_mysql_repository.select_example(column.name, table.name)

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

        return column_info_list

    async def _save_columns_to_qdrant(self, column_info_list: list[ColumnInfo]):

        await self.column_qdrant_repository.ensure_collection()
        # 为每一条数据建立索引，为了能尽可能多的命中索引，这里将数据拆分为多个向量（name,description,alias）
        points: list[dict] = []
        for column_info in column_info_list:
            points.append(
                {"id": uuid.uuid4(),
                 "vector_text": column_info.name,
                 "payload": asdict(column_info)
                 }
            )
            points.append(
                {"id": uuid.uuid4(),
                 "vector_text": column_info.description,
                 "payload": asdict(column_info)
                 }
            )

            [points.append(
                {"id": uuid.uuid4(),
                 "vector_text": alia,
                 "payload": asdict(column_info)
                 }
            ) for alia in column_info.alias]

        embedding_texts = [point["vector_text"] for point in points]

        # 对每个点进行向量化(分批进行)
        # vectors=[self.embedding_client.aembed_documents(vectors[i:i+100]) for i in range(0,len(vectors),100)]

        vectors: list[list[float]] = []
        for i in range(0, len(embedding_texts), 16):
            # 获取当前批次的文本（每批 100 个）
            batch_embedding_texts = embedding_texts[i:i + 16]
            # 调用嵌入模型进行向量化，返回二维列表 [[float, float, ...], ...]
            embedding_results = await self.embedding_client.aembed_documents(batch_embedding_texts)
            # 将向量结果赋值给对应的 point
            vectors.extend(embedding_results)

        ids = [point['id'] for point in points]
        payloads = [point["payload"] for point in points]
        # 进行向量存储
        await self.column_qdrant_repository.upsert(ids=ids, vectors=vectors, payloads=payloads)

    async def _save_columns_to_es(self, meta_config: MetaConfig):
        # 创建索引（类似于mysql数据库创建表）
        await self.value_es_repository.ensure_index()
        values_infos: list[ValueInfo] = []
        for table in meta_config.tables:
            for column in table.columns:
                if column.sync:
                    # 查询字段取值
                    current_column_values = await self.db_mysql_repository.select_example(column.name, table.name,
                                                                                          1000000)
                    current_values_infos = [ValueInfo(id=f'{table.name}.{column.name}.{current_column_value}',
                                                      value=current_column_value,
                                                      column_id=f'{table.name}.{column.name}'
                                                      ) for current_column_value in current_column_values]

                    values_infos.extend(current_values_infos)

        await self.value_es_repository.index(values_infos)

    async def _save_metrics_to_meta_db(self, meta_config: MetaConfig):
        metric_info_list: list[MetricInfo] = []
        column_metric_list: list[ColumnMetric] = []
        for metric in meta_config.metrics:
            metric_info = MetricInfo(
                id=metric.name,
                name=metric.name,
                description=metric.description,
                relevant_columns=metric.relevant_columns,
                alias=metric.alias
            )
            metric_info_list.append(metric_info)

            for column in metric.relevant_columns:
                metric_column_info = ColumnMetric(
                    metric_id=metric.name,
                    column_id=column
                )
                column_metric_list.append(metric_column_info)

        async  with self.meta_mysql_repository.session.begin():
            self.meta_mysql_repository.insert_metric_info(metric_info_list)
            self.meta_mysql_repository.insert_metric_column_info(column_metric_list)
    # 构建方法
    async def build(self, conf_path: Path):
        # 加载元数据配置文件
        context = OmegaConf.load(conf_path)
        schema = OmegaConf.structured(MetaConfig)

        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

        # logger.info(meta_config.metrics)
        # 2 同步配置文件的表数据
        if meta_config.tables:
            # 2.1 将表信息和字段信息同步到数据库中
            column_info_list = await self._save_tables_to_meta_db(meta_config)

            # 2.2 列信息建立向量索引,先创建集合
            await self._save_columns_to_qdrant(column_info_list)

            # 2.3 对指定的维度字段取值建立全文索引
            await self._save_columns_to_es(meta_config)

        # 3 同步配置文件的指标数据
        if meta_config.metrics:
            # 3.1 将配置文件的指标信息同步到数据库中
            await self._save_metrics_to_meta_db(meta_config)

