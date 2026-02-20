from .base_data_model import BaseDataModel
from .db_schemes import DataChunk
from .enums.db_Enum import DB_Enum
from bson.objectid import ObjectId
from pymongo import InsertOne
from typing import Any
from sqlalchemy.future import select
from sqlalchemy import func, delete

class ChunkModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.db_client = db_client
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance 
    
    
    async def create_chunk(self, chunk: DataChunk) -> DataChunk:
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk
    
    
    async def get_chunk(self, chunk_id: int) -> Any:
        async with self.db_client() as session:
            chunk = await session.execute(select(DataChunk).where(DataChunk.chunk_id == chunk_id))
        return chunk.scalar_one_or_none()
        
    
    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int=100) -> int:
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i+batch_size]
                    session.add_all(batch)
            await session.commit()
        return len(chunks)
            
    async def delete_chunks_by_project_id(self, project_id: ObjectId) -> int:
        async with self.db_client() as session:
            stmt = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount
    
    async def get_project_chunks(self, project_id: ObjectId, page_no: int=1, page_size:int=50):
        async with self.db_client() as session:
            stmt = select(DataChunk).where(DataChunk.chunk_project_id == project_id).offset((page_no - 1) * page_size).limit(page_size)
            result = await session.execute(stmt)
            records = result.scalars().all()
        return records
        
    async def get_total_chunks_count(self, project_id: ObjectId) -> int:
        total_count = 0
        async with self.db_client() as session:
            sql_count = select(func.count(DataChunk.chunk_id)).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(sql_count)
            total_count = result.scalar_one()
        return total_count 