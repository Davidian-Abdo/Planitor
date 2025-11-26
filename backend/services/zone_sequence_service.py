"""
FIXED Zone Sequence Service - Compatible with unified session management
"""
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class ZoneSequenceService:
    """
    FIXED Professional service for zone sequence operations
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
    
    def get_zone_sequence_config(self, project_id: int, user_id: int) -> Dict[str, List[List[str]]]:
        """
        Get zone sequence configuration for a project
        """
        try:
            from backend.db.repositories.project_repo import ProjectRepository
            project_repo = ProjectRepository(self.db_session)
            project = project_repo.get_project(project_id, user_id)
            
            if project and hasattr(project, 'zone_sequences') and project.zone_sequences:
                return project.zone_sequences
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting zone sequence config: {e}")
            return {}
    
    def update_zone_sequence(self, project_id: int, user_id: int, 
                           discipline: str, sequence: List[List[str]]) -> bool:
        """
        Update zone sequence for a specific discipline
        """
        try:
            from backend.db.repositories.project_repo import ProjectRepository
            project_repo = ProjectRepository(self.db_session)
            
            # Get current configuration
            current_config = self.get_zone_sequence_config(project_id, user_id)
            
            # Update configuration for the discipline
            current_config[discipline] = sequence
            
            # Save to project
            success = project_repo.update_project(project_id, user_id, {
                'zone_sequences': current_config
            })
            
            if success:
                self.logger.info(f"Updated zone sequence for {discipline} in project {project_id}")
            else:
                self.logger.error(f"Failed to update zone sequence for {discipline}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating zone sequence: {e}")
            return False
        
    def reset_zone_sequence(self, project_id: int, user_id: int) -> bool:
        """
        Reset zone sequence configuration for a project
        """
        try:
            from backend.db.repositories.project_repo import ProjectRepository
            project_repo = ProjectRepository(self.db_session)
            
            success = project_repo.update_project(project_id, user_id, {
                'zone_sequences': {}
            })
            
            if success:
                self.logger.info(f"Reset zone sequence for project {project_id}")
            else:
                self.logger.error(f"Failed to reset zone sequence for project {project_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error resetting zone sequence: {e}")
            return False
    
    def export_zone_sequence(self, project_id: int, user_id: int) -> Dict[str, Any]:
        """
        Export zone sequence configuration
        """
        try:
            config = self.get_zone_sequence_config(project_id, user_id)
            
            export_data = {
                'project_id': project_id,
                'zone_sequences': config,
                'exported_at': self._get_current_timestamp(),
                'version': '1.0'
            }
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error exporting zone sequence: {e}")
            return {}
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for exports"""
        from datetime import datetime
        return datetime.now().isoformat()

    # Additional methods for your existing code compatibility
    def get_project_sequences(self, project_id: int) -> Dict:
        """Compatibility method for existing code"""
        return self.get_zone_sequence_config(project_id, 1)  # Default user_id
    
    def save_project_sequences(self, project_id: int, sequences: Dict, user_id: int) -> bool:
        """Compatibility method for existing code"""
        try:
            from backend.db.repositories.project_repo import ProjectRepository
            project_repo = ProjectRepository(self.db_session)
            
            success = project_repo.update_project(project_id, user_id, {
                'zone_sequences': sequences
            })
            
            return success
        except Exception as e:
            self.logger.error(f"Error saving project sequences: {e}")
            return False
    
    def validate_sequence_configuration(self, config: Dict, available_zones: List[str]) -> Dict:
        """Validate sequence configuration"""
        warnings = []
        
        for discipline, sequence in config.items():
            used_zones = set()
            for group in sequence:
                used_zones.update(group)
            
            # Check for unused zones
            unused_zones = set(available_zones) - used_zones
            if unused_zones:
                warnings.append(f"Zones non utilisées dans '{discipline}': {', '.join(unused_zones)}")
        
        return {'warnings': warnings, 'errors': []}