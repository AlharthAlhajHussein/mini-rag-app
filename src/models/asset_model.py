from .base_data_model import BaseDataModel
from .db_schemes import asset
from .enums.db_Enum import DB_Enum
from bson import ObjectId

class AssetModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = db_client[DB_Enum.COLLECTION_ASSET_NAME.value]
    

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collections()
        return instance 
    
    async def init_collections(self):
        all_collections_names = await self.db_client.list_collection_names()
        if DB_Enum.COLLECTION_ASSET_NAME.value not in all_collections_names:
            await self.db_client.create_collection(DB_Enum.COLLECTION_ASSET_NAME.value)
        indexes = asset.Asset.get_indexes()
        for index in indexes:
            await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])
        
    async def create_asset(self, asset_data: asset.Asset) -> asset.Asset:
        result = await self.collection.insert_one(asset_data.dict(by_alias=True, exclude_unset=True))
        asset_data.id = result.inserted_id
        return asset_data
    
    async def get_all_assets_by_project_id(self, asset_project_id: str, asset_type: str) -> list[asset.Asset]:
        assets_record = self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_type": asset_type
        })
        assets = [asset.Asset(**record) async for record in assets_record]
        return assets

    async def get_asset_record(self, asset_name: str, asset_project_id: str) -> asset.Asset | None:
        record = await self.collection.find_one({
            "asset_name": asset_name,
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id
        })
        if record:
            return asset.Asset(**record)
        return None