from .providers import QdrantDBProvider, PgVectorDBProvider
from .vector_db_enums import VectorDBType
from controllers import BaseController
from sqlalchemy.orm import sessionmaker

class VectorDBProviderFactory:
    
    def __init__(self, config, db_client: sessionmaker = None):
        self.config = config
        self.base_controller = BaseController()
        self.db_client = db_client
    
    def create(self, provider: str):
        if provider == VectorDBType.QDRANT.value:
            qdrant_db_client = self.base_controller.get_database_path(self.config.VECTOR_DB_PATH)
            return QdrantDBProvider(
                db_client=qdrant_db_client, 
                default_distance_method=self.config.VECTOR_DB_DISTANCE_METRIC,
                default_vector_dimension=self.config.EMBEDDING_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD
            )
            
        if provider == VectorDBType.PGVECTOR.value:
            return PgVectorDBProvider(
                db_client=self.db_client, 
                default_distance_method=self.config.VECTOR_DB_DISTANCE_METRIC,
                default_vector_dimension=self.config.EMBEDDING_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD
            )
            
        else:
            raise ValueError(f"Unsupported vector DB provider: {provider}")
        