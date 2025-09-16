from fastapi import UploadFile
from .base_controller import BaseController
from models import ResponseSignals
from .project_controller import ProjectController
import re
import os
class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024
    
    def validate_uploaded_file(self, file: UploadFile):
        
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignals.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignals.FILE_SIZE_EXCEEDED.value
        
        return True, ResponseSignals.FILE_VALIDATED_SUCCESS.value
    
    def generate_unique_file_path(self, project_id: str, orig_file_name: str):
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id)
    
        cleaned_file_name = self.clean_file_name(orig_file_name)
        
        new_file_name = os.path.join(project_path, f"{random_key}_{cleaned_file_name}")

        while os.path.exists(new_file_name):
            random_key = self.generate_random_string()
            new_file_name = os.path.join(project_path, f"{random_key}_{cleaned_file_name}")
        
        return new_file_name, random_key + '_' + cleaned_file_name
    
    def clean_file_name(self, orig_file_name: str):
        
        # remove any spacial characters, except underscore and .
        cleaned_file_name = re.sub(r'[^a-zA-Z0-9_.]', '', orig_file_name.strip())
        
        # replace spaces with underscore 
        cleaned_file_name = cleaned_file_name.replace(' ', '_')
        
        return cleaned_file_name