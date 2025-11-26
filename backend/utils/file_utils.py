"""
Professional file utilities for construction project documents
Handles Excel templates, uploads, and secure file operations
"""
import os
import shutil
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import tempfile
from datetime import datetime

logger = logging.getLogger(__name__)

class FileManager:
    """Professional file management for construction documents"""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'excel': ['.xlsx', '.xls'],
        'image': ['.jpg', '.jpeg', '.png', '.gif'],
        'document': ['.pdf', '.doc', '.docx']
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'excel': 50 * 1024 * 1024,  # 50MB
        'image': 10 * 1024 * 1024,   # 10MB
        'document': 25 * 1024 * 1024 # 25MB
    }
    
    def __init__(self, base_upload_dir: str = "data/uploads"):
        self.base_upload_dir = Path(base_upload_dir)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.base_upload_dir,
            self.base_upload_dir / "templates",
            self.base_upload_dir / "projects",
            self.base_upload_dir / "exports",
            self.base_upload_dir / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate_excel_file(self, file_path: Path, required_sheets: List[str] = None) -> Dict[str, Any]:
        """
        Validate Excel file structure and content for construction templates
        
        Args:
            file_path: Path to Excel file
            required_sheets: List of required sheet names
            
        Returns:
            Dict with validation results
        """
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'sheet_info': {},
            'data_samples': {}
        }
        
        try:
            # Check file exists
            if not file_path.exists():
                validation_result['errors'].append("File does not exist")
                return validation_result
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.MAX_FILE_SIZES['excel']:
                validation_result['errors'].append(f"File too large: {file_size} bytes")
                return validation_result
            
            # Try to read Excel file
            try:
                excel_file = pd.ExcelFile(file_path)
            except Exception as e:
                validation_result['errors'].append(f"Invalid Excel file: {str(e)}")
                return validation_result
            
            # Check required sheets
            if required_sheets:
                missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_file.sheet_names]
                if missing_sheets:
                    validation_result['errors'].append(f"Missing required sheets: {', '.join(missing_sheets)}")
                    return validation_result
            
            # Analyze each sheet
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    sheet_info = {
                        'row_count': len(df),
                        'column_count': len(df.columns),
                        'columns': list(df.columns),
                        'has_data': len(df) > 0
                    }
                    
                    validation_result['sheet_info'][sheet_name] = sheet_info
                    
                    # Store sample data for preview
                    if len(df) > 0:
                        validation_result['data_samples'][sheet_name] = df.head(5).to_dict('records')
                    
                    # Sheet-specific validations
                    if sheet_name.lower() == 'quantities':
                        self._validate_quantity_sheet(df, validation_result)
                    elif sheet_name.lower() == 'resources':
                        self._validate_resource_sheet(df, validation_result)
                        
                except Exception as e:
                    validation_result['warnings'].append(f"Could not read sheet '{sheet_name}': {str(e)}")
            
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            return validation_result
            
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {str(e)}")
            return validation_result
    
    def _validate_quantity_sheet(self, df: pd.DataFrame, validation_result: Dict[str, Any]):
        """Validate quantity matrix sheet"""
        required_columns = ['Discipline', 'Zone', 'Floor', 'Quantity', 'Unit']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation_result['errors'].append(f"Quantity sheet missing columns: {', '.join(missing_columns)}")
        
        # Check for negative quantities
        if 'Quantity' in df.columns:
            negative_quantities = df[df['Quantity'] < 0]
            if len(negative_quantities) > 0:
                validation_result['errors'].append("Negative quantities found in quantity sheet")
    
    def _validate_resource_sheet(self, df: pd.DataFrame, validation_result: Dict[str, Any]):
        """Validate resource sheet"""
        required_columns = ['ResourceType', 'Name', 'Count', 'HourlyRate']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation_result['errors'].append(f"Resource sheet missing columns: {', '.join(missing_columns)}")
    
    def save_uploaded_file(self, uploaded_file, user_id: int, file_type: str) -> Tuple[bool, Path]:
        """
        Save uploaded file with security checks
        
        Args:
            uploaded_file: Streamlit uploaded file object
            user_id: User ID for organization
            file_type: Type of file ('excel', 'image', 'document')
            
        Returns:
            Tuple: (success, file_path)
        """
        try:
            # Validate file type
            file_extension = Path(uploaded_file.name).suffix.lower()
            if file_extension not in self.ALLOWED_EXTENSIONS.get(file_type, []):
                logger.error(f"Invalid file extension: {file_extension} for type {file_type}")
                return False, None
            
            # Create user directory
            user_dir = self.base_upload_dir / "projects" / str(user_id)
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate secure filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{uploaded_file.name}"
            file_path = user_dir / safe_filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            logger.info(f"File saved successfully: {file_path}")
            return True, file_path
            
        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
            return False, None
    
    def cleanup_old_files(self, older_than_hours: int = 24):
        """
        Clean up temporary files older than specified hours
        
        Args:
            older_than_hours: Delete files older than this
        """
        try:
            temp_dir = self.base_upload_dir / "temp"
            cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
            
            files_deleted = 0
            for file_path in temp_dir.glob("*"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    files_deleted += 1
            
            logger.info(f"Cleaned up {files_deleted} temporary files")
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")