from enum import Enum


class VectorDBType(Enum):
    QDRANT = "qdrant"
    PGVECTOR = 'pgvector'


class DistanceMetric(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot"
    MANHATTAN = "manhattan"
    MINKOWSKI = "minkowski"

class PgVectorTableSchemaEnum(Enum):
    ID = "id"
    TEXT = "text"
    VECTOR = "vector"
    CHUNK_ID = "chunk_id"
    METADATA = "metadata"
    _PREFIX = "pgvector"
    
class PgVectorDistanceMethodEnum(Enum):
    COSINE = "vector_cosine_ops"
    EUCLIDEAN = "vector_euclidean_ops"
    DOT_PRODUCT = "vector_l2_ops"


class PgVectorIndexTypeEnum(Enum):
    IVFFLAT = "ivfflat"
    HNSW = "hnsw"
    