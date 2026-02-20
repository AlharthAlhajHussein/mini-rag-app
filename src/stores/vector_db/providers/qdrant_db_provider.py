from ..vector_db_interface import VectorDBInterface
from ..vector_db_enums import DistanceMetric
import logging
from qdrant_client import models, QdrantClient
from qdrant_client.models import PointStruct
from typing import List
import json
from models.db_schemes import RetrievedDocument


class QdrantDBProvider(VectorDBInterface):
    
    def __init__(self, db_client: str, default_distance_method: str, 
                 default_vector_dimension: int = 768,
                 index_threshold: int = 1000):
        
        self.client = None
        self.db_client = db_client
        self.default_vector_dimension = default_vector_dimension
        self.index_threshold = index_threshold
        self.distance_metric = None
        if default_distance_method == DistanceMetric.COSINE.value:
            self.distance_metric = models.Distance.COSINE
        elif default_distance_method == DistanceMetric.DOT_PRODUCT.value:
            self.distance_metric = models.Distance.DOT
        elif default_distance_method == DistanceMetric.EUCLIDEAN.value:
            self.distance_metric = models.Distance.EUCLIDEAN
        self.logger = logging.getLogger("uvicorn")
        
        
    async def connect(self):
        self.client = QdrantClient(path=self.db_client)
        self.logger.info("Connected to Qdrant database at %s", self.db_client)
    
    async def disconnect(self):
        self.client = None
        self.logger.info("Disconnected from Qdrant database")
    
    async def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    async def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    async def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    async def delete_collection(self, collection_name: str):
        if not await self.is_collection_exists(collection_name):
            self.logger.warning("Collection %s does not exist. Cannot delete.", collection_name)
            return
        return self.client.delete_collection(collection_name=collection_name)
    
    async def create_collection(self, collection_name: str, dimension: int, do_reset: bool = False):
        
        if do_reset:
            _ = await self.delete_collection(collection_name)
        
        if not await self.is_collection_exists(collection_name):
            self.logger.info("Creating new Qdrant collection %s with dimension %d and distance metric %s", collection_name, dimension, self.distance_metric)
            self.client.create_collection(
                collection_name = collection_name,
                vectors_config = models.VectorParams(
                    size= dimension,
                    distance= self.distance_metric
                )
            )
            return True
        return False
    
    async def insert_one(self, collection_name: str,
                   text: str,
                   vector: List[float],
                   record_id: str,
                   metadata: dict= None):
        
        if not await self.is_collection_exists(collection_name):
            self.logger.error("Collection %s does not exist. Cannot insert data.", collection_name)
            return False
        
        try:
            _ = self.client.upsert(
                collection_name= collection_name,
                wait=True,
                points= [
                    PointStruct(
                        id=record_id,
                        vector=vector,
                        payload= {
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error("Error inserting record: %s", str(e))
            return False
        return True
        
    async def insert_many(self, collection_name: str,
                    texts: List[str],
                    vectors: List[List[float]],
                    record_ids: List[str],
                    metadatas: List[dict]= None,
                    batch_size: int= 50) -> bool:
                        
        if metadatas is None:
            metadatas = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))
        
        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]
            
            points = []
            for text, vector, record_id, metadata in zip(batch_texts, batch_vectors, batch_record_ids, batch_metadatas):
                point = PointStruct(
                    id= record_id,
                    vector= vector,
                    payload= {
                        "text": text,
                        "metadata": metadata
                    }
                )
                points.append(point)
            
            try:
                _ = self.client.upload_points(
                    collection_name= collection_name,
                    points=points
                )
            except Exception as e:
                self.logger.error("Error inserting batch starting at index %d: %s", i, str(e))
                return False
        return True
    

    async def search_by_vector(self, collection_name: str,
                         query_vector: List[float],
                         top_k: int= 5) -> List[dict]:
        
        
        results = self.client.query_points(
            collection_name= collection_name,
            query= query_vector,
            limit= top_k
        )
        
        if not results.points:
            return []
        
        return [
            RetrievedDocument(**{
                "score": result.score,
                "text": result.payload['text']
            })
            for result in results.points
        ]
        
        
        
        
        
            

                    
        
        