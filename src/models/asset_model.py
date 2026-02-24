from .base_data_model import BaseDataModel
from .db_schemes import Asset
from .enums.db_Enum import DB_Enum
from bson import ObjectId
from sqlalchemy.future import select
from sqlalchemy import func

class AssetModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.db_client = db_client    

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance 

        
    async def create_asset(self, asset: Asset) -> Asset:
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset)
        return asset
    
    
    async def get_all_assets_by_project_id(self, asset_project_id: int, asset_type: str) -> list[Asset]:
        async with self.db_client() as session:
            stmt = select(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.asset_type == asset_type
            )
            result = await session.execute(stmt)
            assets = result.scalars().all()
            return assets
        
        
    async def get_asset_record(self, asset_id: int, asset_project_id: int) -> Asset | None:
        async with self.db_client() as session:
            stmt = select(Asset).where(
                Asset.asset_id == asset_id,
                Asset.asset_project_id == asset_project_id
            )
            result = await session.execute(stmt)
            asset = result.scalar_one_or_none()
            return asset