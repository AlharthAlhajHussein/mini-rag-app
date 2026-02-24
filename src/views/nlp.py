from pydantic import BaseModel
from typing import List
from models.db_schemes.minirag.schemes.data_chunk import RetrievedDocument


class NLPPushResponse(BaseModel):
    inserted_items_count: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "inserted items count": 50
            }
        }
    }
    
class NLPInfoResponse(BaseModel):
    collection_info: dict
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "collection_info": {
                    "table_info": {
                        "schemaname": "public",
                        "tablename": "collection_768_8",
                        "tableowner": "alharth",
                        "tablespace": "null",
                        "hasindexes": "true"
                    },
                    "count": 22
                }
            }
        }
    }
    

class NLPSearchResponse(BaseModel):
    results: List[RetrievedDocument]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "results": [
                    {
                        "text": "This is a sample chunk of text.",
                        "score": 0.95
                    },
                    {
                        "text": "Another relevant chunk of information.",
                        "score": 0.89
                    }
                ]
            }
        }
    }
    
    
class NLPAnswerResponse(BaseModel):
    answer: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "This is a generated answer based on the retrieved documents and the query."
            }
        }
    }