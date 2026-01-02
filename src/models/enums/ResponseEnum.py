from enum import Enum


class ResponseSignals(Enum):
    
    
    FILE_VALIDATED_SUCCESS = "file validated successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file size exceeded"
    FILE_UPLOAD_SUCCESS = "file upload success"
    FILE_UPLOAD_FAILED = "file upload failed"
    
    FILE_PROCESSING_FAILED = "file processing failed"
    FILE_PROCESSING_SUCCESS = "file processing success"
    
    NO_FILES_TO_PROCESS = "no files to process"
    FILE_NOT_FOUND = "file not found with given id"
    