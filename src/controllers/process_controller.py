from .base_controller import BaseController
from .project_controller import ProjectController
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingFiles
import os
import logging

logger = logging.getLogger(__name__)

class ProcessController(BaseController):
    
    def __init__(self, project_id: str):
        super().__init__()
        
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id)
        
    
    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self, file_id: str):
        
        file_extension = self.get_file_extension(file_id)
        
        file_path = os.path.join(self.project_path, file_id)
        
        if file_extension == ProcessingFiles.TXT.value:
            return TextLoader(file_path, encoding='utf-8')
        elif file_extension == ProcessingFiles.PDF.value:
            return PyMuPDFLoader(file_path)
        
        return None
    
    def get_file_content(self, file_id: str):
        
        loader = self.get_file_loader(file_id)
        
        if not loader:
            return None
        
        try:
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading file {file_id}: {e}")
            return None
    
    def process_file_content(self, file_content: list, file_id: str, chunk_size: int = 100, chunk_overlap: int = 20):
        
        if not file_content:
            return None
        
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
        file_page_content = [doc.page_content for doc in file_content]
        file_content_metadata = [doc.metadata for doc in file_content]
        

        chunks = text_splitter.create_documents(file_page_content, metadatas=file_content_metadata)
        
        return chunks
    