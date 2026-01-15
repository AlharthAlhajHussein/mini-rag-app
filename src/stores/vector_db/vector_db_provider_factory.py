from .providers import QdrantDBProvider
from .vector_db_enums import VectorDBType
from controllers import BaseController


class VectorDBProviderFactory:
    
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()
    
    def create(self, provider: str):
        if provider == VectorDBType.QDRANT.value:
            db_path = self.base_controller.get_database_path(self.config.VECTOR_DB_PATH)
            distance = self.config.VECTOR_DB_DISTANCE_METRIC
            return QdrantDBProvider(db_path=db_path, distance=distance)
        else:
            raise ValueError(f"Unsupported vector DB provider: {provider}")
        