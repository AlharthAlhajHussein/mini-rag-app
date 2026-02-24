from pydantic import BaseModel, Field
from typing import Optional

class ProcessRequest(BaseModel):
    
    file_id: Optional[int] = Field(default=None, description="The ID of the file to process. If not provided, all unprocessed files for the project will be processed.")
    chunk_size: Optional[int] = Field(default=500, description="The size of each chunk in characters")
    overlap_size: Optional[int] = Field(default=30, description="The overlap size between chunks in characters")
    do_reset: Optional[bool] = Field(default=False, description="Whether to reset the existing chunks in the database before processing new data")
    

    model_config = {
        "json_schema_extra": {
            "example": {
                "file_id": 123,
                "chunk_size": 500,
                "overlap_size": 30,
                "do_reset": False
            }
        }
    }

