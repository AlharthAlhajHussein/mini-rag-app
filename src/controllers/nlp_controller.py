from .base_controller import BaseController
from models.db_schemes import Project, DataChunks
from typing import List
from stores.llm.llm_enums import DocumentTypeEnums
import json

class NLPCntroller(BaseController):
    
    def __init__(self, vector_db_client, generation_client, embedding_client):
        super().__init__()

        self.vector_db_client = vector_db_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        
    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vector_db_client.delete_collection(collection_name=collection_name)
    
    def get_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vector_db_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info, default=lambda o: o.__dict__)
        )
    
    def index_into_vector_db(self, project: Project, chunks: List[DataChunks], chunks_ids: List[int], do_reset: bool=False):
                
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # step2: manage items
        texts = [c.chunk_text for c in chunks]
        metadatas = [c.chunk_metadata for c in chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnums.DOCUMENT.value)
            for text in texts
        ]
        
        
        # step3: create collection if not exists
        _ = self.vector_db_client.create_collection(
            collection_name=collection_name,
            dimension=self.embedding_client.embedding_size,
            do_reset=do_reset
        )    
        
        # step4: insert into vector db
        _= self.vector_db_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadatas=metadatas,
            vectors=vectors,
            record_ids=chunks_ids
        )
        
        return True
    
    def search_vector_db_collection(self, project: Project, query_text: str, top_k: int=5):
        
        
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # step2: get text embedding vector
        vector = self.embedding_client.embed_text(text=query_text, document_type=DocumentTypeEnums.QUERY.value)
        
        if not vector or len(vector) == 0:
            return False
        
        # step3: do semantic search
        results = self.vector_db_client.search_by_vector(
            collection_name= collection_name,
            query_vector= vector,
            top_k= top_k
        )
        
        if not results:
            return False
        
        return json.loads(
            json.dumps(results, default=lambda o: o.__dict__)
        )
        
        