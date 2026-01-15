from enum import Enum


class VectorDBType(Enum):
    FAISS = "faiss"
    MILVUS = "milvus"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    CHROMA = "chroma"
    QDRANT = "qdrant"


class DistanceMetric(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot"
    MANHATTAN = "manhattan"
    MINKOWSKI = "minkowski"
    