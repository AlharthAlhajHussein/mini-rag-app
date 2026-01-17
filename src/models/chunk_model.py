from .base_data_model import BaseDataModel
from .db_schemes import DataChunks
from .enums.db_Enum import DB_Enum
from bson.objectid import ObjectId
from pymongo import InsertOne
from typing import Any

class ChunkModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = db_client[DB_Enum.COLLECTION_CHUNK_NAME.value]
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collections()
        return instance 
    
    async def init_collections(self):
        all_collections_names = await self.db_client.list_collection_names()
        if DB_Enum.COLLECTION_CHUNK_NAME.value not in all_collections_names:
            await self.db_client.create_collection(DB_Enum.COLLECTION_CHUNK_NAME.value)
        indexes = DataChunks.get_indexes()
        for index in indexes:
            await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])
           
    async def create_chunk(self, chunk_data: DataChunks) -> DataChunks:
        result = await self.collection.insert_one(chunk_data.dict(by_alias=True, exclude_unset=True))
        chunk_data.id = result.inserted_id
        return chunk_data
    
    async def get_chunk(self, chunk_id: str) -> Any:
        
        result = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if result:
            return DataChunks(**result)
        return None
    
    async def insert_many_chunks(self, chunks: list[DataChunks], batch_size: int=100) -> int:
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            operations = [InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in batch]
            
            result = await self.collection.bulk_write(operations)
            
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId) -> int:
        
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count
    
    
    async def get_project_chunks(self, project_id: ObjectId, page_no: int=1, page_size:int=50):
        records = await self.collection.find({
            "chunk_project_id": project_id
        }).skip((page_no - 1) * page_size).limit(page_size).to_list(None)
                
        return [
            DataChunks(**record)
            for record in records
        ]
        
        
        