from ..vector_db_interface import VectorDBInterface
from ..vector_db_enums import PgVectorTableSchemaEnum, PgVectorDistanceMethodEnum, PgVectorIndexTypeEnum, DistanceMetric
from models.db_schemes import RetrievedDocument
import logging
from typing import List
from sqlalchemy.sql import text as sql_text
import json

class PgVectorDBProvider(VectorDBInterface):
    def __init__(self, db_client, default_vector_dimension: int = 768,
                 default_distance_method: str = None, index_threshold: int = 1000):
        self.db_client = db_client
        self.default_vector_dimension = default_vector_dimension
        
        if default_distance_method == DistanceMetric.COSINE.value:
            default_distance_method = PgVectorDistanceMethodEnum.COSINE.value
        elif default_distance_method == DistanceMetric.DOT_PRODUCT.value:
            default_distance_method = PgVectorDistanceMethodEnum.DOT_PRODUCT.value
            
        self.default_distance_method = default_distance_method
        self.index_threshold = index_threshold
        
        self.pgvector_table_prefix = PgVectorTableSchemaEnum._PREFIX.value
        self.logger = logging.getLogger("uvicorn")
        self.default_index_name = lambda collection_name: f"{collection_name}_vector_idx"
        
    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE EXTENSION IF NOT EXISTS vector"
                ))
                await session.commit()
        self.logger.info("Connected to PostgreSQL database and ensured vector extension is available.")
    
    async def disconnect(self):
        pass
    
    async def is_collection_exists(self, collection_name: str) -> bool:
        record = None
        async with self.db_client() as session:
            async with session.begin():
                list_tables = sql_text("SELECT * FROM pg_tables WHERE tablename = :collection_name")
                results = await session.execute(list_tables, {"collection_name": collection_name})
                record = results.scalar_one_or_none()
            return record
    
    async def list_all_collections(self) -> List:
        records = []
        async with self.db_client() as session:
            async with session.begin():
                list_tables = sql_text("SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix")
                results = await session.execute(list_tables, {"prefix": f"{self.pgvector_table_prefix}%"})
                records = results.scalars().all()
            return records
    
    async def get_collection_info(self, collection_name: str) -> dict:
         async with self.db_client() as session:
            async with session.begin():
                
                table_info_sql = sql_text("""
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                    FROM pg_tables
                    WHERE tablename = :collection_name
                """)
                count_sql = sql_text(f"SELECT COUNT(*) FROM {collection_name}")
                
                table_info = await session.execute(table_info_sql, {"collection_name": collection_name})
                record_count = await session.execute(count_sql)
                
                row = table_info.fetchone()
                count = record_count.scalar_one()
                
                if not row:
                    return None
                return {
                    "table_info": dict(row._mapping),
                    "count": count
                }
    
    async def delete_collection(self, collection_name: str) -> bool:
        if not await self.is_collection_exists(collection_name):
            self.logger.warning("Collection %s does not exist. Cannot delete.", collection_name)
            return False 
        async with self.db_client() as session:
            async with session.begin():
                delete_sql = sql_text(f"DROP TABLE IF EXISTS {collection_name}")
                await session.execute(delete_sql)
                await session.commit()
        return True
    
    async def create_collection(self, collection_name: str, dimension: int, do_reset: bool = False) -> bool:
        if do_reset:
            _ = await self.delete_collection(collection_name)
        
        is_collection_exists = await self.is_collection_exists(collection_name)
        if not is_collection_exists:
            self.logger.info("Creating collection %s with dimension %d", collection_name, dimension)
            async with self.db_client() as session:
                async with session.begin():
                    create_table_sql = sql_text(f"""
                        CREATE TABLE {collection_name} (
                            {PgVectorTableSchemaEnum.ID.value} BIGSERIAL PRIMARY KEY,
                            {PgVectorTableSchemaEnum.TEXT.value} TEXT,
                            {PgVectorTableSchemaEnum.VECTOR.value} VECTOR({dimension}),
                            {PgVectorTableSchemaEnum.METADATA.value} JSONB DEFAULT '{{}}',
                            {PgVectorTableSchemaEnum.CHUNK_ID.value} INTEGER,
                            FOREIGN KEY ({PgVectorTableSchemaEnum.CHUNK_ID.value}) REFERENCES chunks(chunk_id) ON DELETE CASCADE
                        )
                    """)
                    await session.execute(create_table_sql)
                    await session.commit()
            return True
        return False

    async def is_index_exists(self, collection_name: str) -> bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                index_info_sql = sql_text("""
                    SELECT 1
                    FROM pg_indexes
                    WHERE tablename = :collection_name 
                    AND indexname = :index_name
                """)
                result = await session.execute(index_info_sql, {"collection_name": collection_name, "index_name": index_name})
                index_info = result.scalar_one_or_none()
                return bool(index_info)
        
    async def create_vector_index(self, collection_name: str, 
                                  index_type: str = PgVectorIndexTypeEnum.HNSW.value) -> bool:
        
        is_index_exists = await self.is_index_exists(collection_name)
        if is_index_exists:
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                count_sql = sql_text(f"SELECT COUNT(*) FROM {collection_name}")
                result = await session.execute(count_sql)
                count = result.scalar_one()
                if count < self.index_threshold:
                    return False
                
                self.logger.info("Creating vector index for collection %s with index type %s", collection_name, index_type)
                
                index_name = self.default_index_name(collection_name)
                create_index_sql = sql_text(f"""
                    CREATE INDEX {index_name} ON {collection_name}
                    USING {index_type} ({PgVectorTableSchemaEnum.VECTOR.value} {self.default_distance_method});
                """)
                await session.execute(create_index_sql)
                await session.commit()
                
                self.logger.info("End creating vector index for collection %s with index type %s", collection_name, index_type)
        return True
    
    async def reset_vector_index(self, collection_name: str, 
                                 index_type: str = PgVectorIndexTypeEnum.HNSW.value) -> bool:
        is_index_exists = await self.is_index_exists(collection_name)
        if is_index_exists:
            async with self.db_client() as session:
                async with session.begin():
                    index_name = self.default_index_name(collection_name)
                    drop_index_sql = sql_text("""
                        DROP INDEX IF EXISTS :index_name
                    """)
                    await session.execute(drop_index_sql, {"index_name": index_name})
                    await session.commit()
            self.logger.info("Dropped existing index %s for collection %s", index_name, collection_name)
        
        created = await self.create_vector_index(collection_name, index_type)
        return created
        
    async def insert_one(self, collection_name: str,
                         text: str,
                         vector: List[float],
                         metadata: dict= None,
                         record_id: str= None) -> bool:
        
        is_collection_exists = await self.is_collection_exists(collection_name)
        if not is_collection_exists:
            self.logger.error("Collection %s does not exist. Cannot insert data.", collection_name)
            return False
        if not record_id:
            self.logger.error("Can not insert new record (vector and text) without record_id (chunk_id) %s.", collection_name)
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(f"""
                    INSERT INTO "{collection_name}" ({PgVectorTableSchemaEnum.TEXT.value}, {PgVectorTableSchemaEnum.VECTOR.value}, {PgVectorTableSchemaEnum.METADATA.value}, {PgVectorTableSchemaEnum.CHUNK_ID.value})
                    VALUES (:text, :vector, :metadata, :chunk_id)
                """)
                await session.execute(insert_sql, {
                    "text": text,
                    "vector": "[" + ",".join(map(str, vector)) + "]",
                    "metadata": metadata,
                    "chunk_id": record_id
                })
                await session.commit()
        await self.create_vector_index(collection_name)
        return True
    
    async def insert_many(self, collection_name: str,
                          texts: List[str],
                          vectors: List[List[float]],
                          metadatas: List[dict]= None,
                          record_ids: List[str]= None,
                          batch_size: int= 50) -> bool:
        
        is_collection_exists = await self.is_collection_exists(collection_name)
        if not is_collection_exists:
            self.logger.error("Collection %s does not exist. Cannot insert data.", collection_name)
            return False

        if len(vectors) != len(record_ids) or len(texts) != len(record_ids):
            self.logger.error("Invalid Length the vectors, texts and record_ids must be the same in collection: %s.", collection_name, "Cannot insert data.")
            return False

        if not metadatas or len(metadatas) == 0:
            metadatas = [None] * len(texts)
        
        async with self.db_client() as session:
            async with session.begin():
                batch_insert_sql = sql_text(f"""
                    INSERT INTO "{collection_name}" (
                        {PgVectorTableSchemaEnum.TEXT.value},
                        {PgVectorTableSchemaEnum.VECTOR.value}, 
                        {PgVectorTableSchemaEnum.METADATA.value}, 
                        {PgVectorTableSchemaEnum.CHUNK_ID.value})
                    VALUES (:text, :vector, :metadata, :chunk_id)
                """)
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i+batch_size]
                    batch_vectors = vectors[i:i+batch_size]
                    batch_metadatas = metadatas[i:i+batch_size] if metadatas else [None]*len(batch_texts)
                    batch_record_ids = record_ids[i:i+batch_size]

                    values = []
                    for _text, _vector, _metadata, _chunk_id in zip(batch_texts, batch_vectors, batch_metadatas, batch_record_ids):
                        values.append({
                            "text": _text,
                            "vector": "[" + ",".join(map(str, _vector)) + "]",
                            "metadata": json.dumps(_metadata) if _metadata else None, # Ensure JSON string,
                            "chunk_id": _chunk_id
                        })
                    
                    await session.execute(batch_insert_sql, values)
                    
        await self.create_vector_index(collection_name)
        
        return True
    
    async def search_by_vector(self, collection_name: str,
                         query_vector: List[float],
                         top_k: int= 10,
                         filter: dict= None) -> List[RetrievedDocument]:
        
        is_collection_exists = await self.is_collection_exists(collection_name)
        if not is_collection_exists:
            self.logger.error("Collection %s does not exist. Cannot search data.", collection_name)
            return False
                
        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(f"""
                    SELECT {PgVectorTableSchemaEnum.TEXT.value} as text, 1 - ({PgVectorTableSchemaEnum.VECTOR.value} <=> :vector) as score
                    FROM "{collection_name}"
                    ORDER BY score DESC
                    LIMIT :top_k
                """)
                results = await session.execute(search_sql, {
                    "vector": "[" + ",".join(map(str, query_vector)) + "]",
                    "top_k": top_k
                })
                records = results.fetchall()
            
        return [
            RetrievedDocument(**{
                "text": record.text,
                "score": record.score
            })
            for record in records
        ]
                