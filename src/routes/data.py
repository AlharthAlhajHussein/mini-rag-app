from fastapi import APIRouter, Depends, UploadFile, status, Request, HTTPException
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController, ProcessController
from models import ResponseSignals, AssetTypeEnum, ProjectModel, ChunkModel, AssetModel
import os
import aiofiles
import logging
from .schemes import ProcessRequest
from models.db_schemes import DataChunk, Asset
from controllers import NLPCntroller
from views.data import UploadDataResponse, ProcessDataResponse

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix='/api/v1/data',
    tags=['data']
)

@data_router.post(
    "/upload/{project_id}",
    response_model = UploadDataResponse,
    status_code= status.HTTP_201_CREATED,
    responses= {
        400: {
            "description": "Bad Request - Invalid file",
            "content": {
                "application/json": {
                    "example": {
                        "FileTypeNotSupported": ResponseSignals.FILE_TYPE_NOT_SUPPORTED.value,
                        "FileSizeExceeded": ResponseSignals.FILE_SIZE_EXCEEDED.value
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": ResponseSignals.FILE_UPLOAD_FAILED.value
                    }
                }
            }
        }
    },
    summary="Upload a file to a specific project",
    description="""Upload a file to a specific project. The file will be validated for type and size based on the application settings. If the file is valid, it will be saved to the server's file system and a record will be created in the database linking the file to the project. The response will include the file name, project ID, and file ID. If the file is invalid or if there is an error during upload, an appropriate error message will be returned."""
)
async def upload_data(request: Request, project_id: int, file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)):
    
    data_controller = DataController()
    
    # validate the file properties
    is_valid, result_signal = data_controller.validate_uploaded_file(file)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result_signal
        )
        
    file_path, file_id = data_controller.generate_unique_file_path(str(project_id), file.filename)
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseSignals.FILE_UPLOAD_FAILED.value
        )
    
    project_model = await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id)
    
    asset_model = await AssetModel.create_instance(request.app.db_client)
    asset_resource = Asset(
        asset_project_id=project.project_id,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
        asset_type=AssetTypeEnum.FILE.value,
    )
    asset_record = await asset_model.create_asset(asset_resource)
    
    
    return UploadDataResponse(
        file_name=str(asset_record.asset_name),
        project_id=str(asset_record.asset_project_id),
        file_id=str(asset_record.asset_id),
    )
    
@data_router.post(
    "/process/{project_id}",
    response_model=ProcessDataResponse,
    status_code= status.HTTP_200_OK,
    responses= {
        404: {
            "description": "Not Found - File not found or no files to process",
            "content": {
                "application/json": {
                    "example": {
                        "FileNotFound": ResponseSignals.FILE_NOT_FOUND.value + ": 3",
                        "NoFilesToProcess": ResponseSignals.NO_FILES_TO_PROCESS.value
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error - File processing failed",
            "content": {
                "application/json": {
                    "example": {
                        "FileProcessingFailed": ResponseSignals.FILE_PROCESSING_FAILED.value
                    }
                }
            }
        }
    },
    summary="Process uploaded files for a specific project",
    description="""Process the uploaded files for a given project. This endpoint will read the content of the files, split them into chunks based on the specified chunk size and overlap, and store the chunks in the database. If a file_id is provided in the request body, only that file will be processed. If no file_id is provided, all files associated with the project will be processed. The endpoint also supports an optional reset flag that, when set to true, will clear all existing chunks for the project before processing the files."""
)
async def process_endpoint(request: Request, project_id: int, process_request: ProcessRequest):
    
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    
    project_model = await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id)
    
    nlp_controller = NLPCntroller(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )
    
    process_controller = ProcessController(project_id)
    
    asset_model = await AssetModel.create_instance(request.app.db_client)

    project_files_ids = {}
    if file_id:
        asset_record = await asset_model.get_asset_record(file_id, project.project_id)
        if asset_record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ResponseSignals.FILE_NOT_FOUND.value + f": {file_id}"
            )

        project_files_ids[asset_record.asset_id] = asset_record.asset_name
    else:
        assets = await asset_model.get_all_assets_by_project_id(project.project_id, AssetTypeEnum.FILE.value)
        project_files_ids = {asset.asset_id : asset.asset_name for asset in assets}

    if project_files_ids is None or len(project_files_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.NO_FILES_TO_PROCESS.value
        )
        
    no_records = 0
    no_files_processed = 0
    
    chunk_model = await ChunkModel.create_instance(request.app.db_client)
    
    if do_reset:
        # delete vector db collection
        collection_name = nlp_controller.create_collection_name(project_id=project.project_id)
        _ = await nlp_controller.vector_db_client.delete_collection(collection_name=collection_name)
        
        # delete chunks from db
        _ = await chunk_model.delete_chunks_by_project_id(project.project_id)


    for asset_id, file_id in project_files_ids.items():
        file_content = process_controller.get_file_content(file_id)
        
        if file_content is None:
            logger.error(f"File content not found for file_id: {file_id}")
            continue
        
            
        file_chunks = process_controller.process_file_content(file_content, file_id,
                                                            chunk_size=chunk_size,
                                                            chunk_overlap=overlap_size)
        if file_chunks is None or len(file_chunks) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ResponseSignals.FILE_PROCESSING_FAILED.value
            )
        
        
        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=index + 1,
                chunk_project_id=project.project_id,
                chunk_asset_id=asset_id
            ) for index, chunk in enumerate(file_chunks)
        ]
        
        
        no_records += await chunk_model.insert_many_chunks(file_chunks_records)
        no_files_processed += 1

    return ProcessDataResponse(
        added_chunks=no_records,
        files_processed=no_files_processed
    )
     