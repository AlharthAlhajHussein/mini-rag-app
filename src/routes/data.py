from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController
from models import ResponseSignals
import os
import aiofiles
import logging

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix='/api/v1/data',
    tags=['api_v1', 'data']
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)):
    
    data_controller = DataController()
    
    # validate the file properties
    is_valid, result_signal = data_controller.validate_uploaded_file(file)
    
    
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'signal': result_signal}
        )
        
    file_path = data_controller.generate_unique_file_name(project_id, file.filename)
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'signal': ResponseSignals.FILE_UPLOAD_FAILED.value}
        )
            
    return JSONResponse(
        content={'signal': ResponseSignals.FILE_UPLOAD_SUCCESS.value}
    )
    