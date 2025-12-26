from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController, ProcessController
from models import ResponseSignals
import os
import aiofiles
import logging
from .schemes import ProcessRequest

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
        
    file_path, file_id = data_controller.generate_unique_file_path(project_id, file.filename)
    
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
        content={'signal': ResponseSignals.FILE_UPLOAD_SUCCESS.value,
                 'file_id': file_id}
    )
    

@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, process_request: ProcessRequest):
    
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    
    process_controller = ProcessController(project_id)
    
    file_content = process_controller.get_file_content(file_id)
        
    file_chunks = process_controller.process_file_content(file_content, file_id,
                                                     chunk_size=chunk_size,
                                                        chunk_overlap=overlap_size)
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'signal': ResponseSignals.FILE_PROCESSING_FAILED.value}
        )
    
    return file_chunks
    