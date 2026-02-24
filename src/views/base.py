from pydantic import BaseModel



class BaseResponse(BaseModel):
    app_name: str
    app_version: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "app_name": "Mini RAG Application",
                "app_version": "1.0.0"
            }
        }
    }