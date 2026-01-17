from ..vector_db_interface import VectorDBInterface
from ..vector_db_enums import DistanceMetric
import logging
from qdrant_client import models, QdrantClient
from qdrant_client.models import PointStruct
from typing import List
import json


class QdrantDBProvider(VectorDBInterface):
    
    def __init__(self, db_path: str, distance: str):
        
        self.client = None
        self.db_path = db_path
        self.distance_metric = None
        if distance == DistanceMetric.COSINE.value:
            self.distance_metric = models.Distance.COSINE
        elif distance == DistanceMetric.DOT_PRODUCT.value:
            self.distance_metric = models.Distance.DOT
        elif distance == DistanceMetric.EUCLIDEAN.value:
            self.distance_metric = models.Distance.EUCLIDEAN
        self.logger = logging.getLogger(__name__)
        
        
    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        self.logger.info("Connected to Qdrant database at %s", self.db_path)
    
    def disconnect(self):
        self.client = None
        self.logger.info("Disconnected from Qdrant database")
    
    def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str):
        if not self.is_collection_exists(collection_name):
            self.logger.warning("Collection %s does not exist. Cannot delete.", collection_name)
            return
        return self.client.delete_collection(collection_name=collection_name)
    
    def create_collection(self, collection_name: str, dimension: int, do_reset: bool = False):
        
        if do_reset:
            _ =self.delete_collection(collection_name)
        
        if not self.is_collection_exists(collection_name):
            self.client.create_collection(
                collection_name = collection_name,
                vectors_config = models.VectorParams(
                    size= dimension,
                    distance= self.distance_metric
                )
            )
            return True
        return False
    
    def insert_one(self, collection_name: str,
                   text: str,
                   vector: List[float],
                   record_id: str,
                   metadata: dict= None):
        
        if not self.is_collection_exists(collection_name):
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
        
    def insert_many(self, collection_name: str,
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
    

    def search_by_vector(self, collection_name: str,
                         query_vector: List[float],
                         top_k: int= 5) -> List[dict]:
        
        
        return self.client.query_points(
            collection_name= collection_name,
            query= query_vector,
            limit= top_k
        )
            

                    
        
        