from .base_data_model import BaseDataModel
from .db_schemes import Project
from .enums.db_Enum import DB_Enum


class ProjectModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = db_client[DB_Enum.COLLECTION_PROJECT_NAME.value]
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collections()
        return instance 
    
    async def init_collections(self):
        all_collections_names = await self.db_client.list_collection_names()
        if DB_Enum.COLLECTION_PROJECT_NAME.value not in all_collections_names:
            await self.db_client.create_collection(DB_Enum.COLLECTION_PROJECT_NAME.value)
        indexes = Project.get_indexes()
        for index in indexes:
            await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])
        
    async def create_project(self, project_data: Project) -> Project:
        result = await self.collection.insert_one(project_data.dict(by_alias=True, exclude_unset=True))
        project_data.id = result.inserted_id
        return project_data
    
    async def get_project_or_create_one(self, project_id: str) -> Project:
        
        project_data = await self.collection.find_one({"project_id": project_id})
        
        if project_data:
            return Project(**project_data)
        
        new_project = Project(project_id=project_id)
        created_project = await self.create_project(new_project)
        return created_project 
     
    async def get_all_projects(self, page: int=1, page_size: int=10) -> list[Project]:
        total_documents = self.collection.count_documents({})
        
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1
        
        
        projects = []
        cursor = self.collection.find({}).skip((page - 1) * page_size).limit(page_size)
        async for project_data in cursor:
            projects.append(Project(**project_data))
        
        return projects, total_pages
    