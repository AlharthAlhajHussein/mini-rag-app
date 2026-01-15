from abc import ABC, abstractmethod
from typing import List



class VectorDBInterface(ABC):
    
    
    @abstractmethod
    def connect(self):
        """Establish a connection to the vector database."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close the connection to the vector database."""
        pass
    
    @abstractmethod
    def is_collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists in the vector database."""
        pass
    
    @abstractmethod
    def list_all_collections(self) -> List:
        """List all collections in the vector database."""
        pass
    
    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        """Get information about a specific collection."""
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a specific collection from the vector database."""
        pass
    
    @abstractmethod
    def create_collection(self, collection_name: str, dimension: int, do_reset: bool=False) -> bool:
        """Create a new collection in the vector database."""
        pass
    
    @abstractmethod
    def insert_one(self, collection_name: str,
                   text: str,
                   vector: List[float],
                   metadata: dict= None,
                   record_id: str= None) -> bool:
        """Insert a single vector or a piece of text into a specific collection."""
        pass
    
    @abstractmethod
    def insert_many(self, collection_name: str,
                    texts: List[str],
                    vectors: List[List[float]],
                    metadatas: List[dict]= None,
                    record_ids: List[str]= None,
                    batch_size: int= 50) -> bool:
        """Insert multiple vectors or pieces of text into a specific collection."""
        pass
    
    @abstractmethod
    def search_by_vector(self, collection_name: str,
                         query_vector: List[float],
                         top_k: int= 10,
                         filter: dict= None) -> List[dict]:
        """Search for similar vectors in a specific collection using a query vector."""
        pass
    
    