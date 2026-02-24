from pydantic import BaseModel, Field
from typing import Optional


class PushRequest(BaseModel):
    do_reset: Optional[bool] = Field(default=False, description="Whether to reset the existing collection in vector db before pushing new data")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "do_reset": False
            }
        }
    }

class SearchRequest(BaseModel):
    query_text: str = Field(..., description="The text query to search for relevant chunks in vector db collection")
    top_k: Optional[int] = Field(default=5, description="The number of top relevant chunks to return from the search results")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query_text": "Who is Nikola Tesla?",
                "top_k": 5
            }
        }
    }