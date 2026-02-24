from pydantic import BaseModel




class UploadDataResponse(BaseModel):
    file_name: str
    project_id: str
    file_id: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "file_name": "lelPMjsnty3T_.txt",
                "project_id": "2",
                "file_id": "7"
            }
        }
    }
    

class ProcessDataResponse(BaseModel):
    added_chunks: int
    files_processed: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "added_chunks": 20,
                "files_processed": 1
            }
        }
    }