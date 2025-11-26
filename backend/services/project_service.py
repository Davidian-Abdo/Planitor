"""
PROFESSIONAL Project Service - PRODUCTION READY
Enhanced with proper zones format handling and transaction awareness
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from backend.utils.error_handler import error_decorator, AppError
from backend.utils.validators import Validator

logger = logging.getLogger(__name__)

class ProjectService:
    """
    Production-ready project management service
    Handles data flow between frontend, domain models, and database
    Enhanced with proper zones format: {zone_name: {max_floors: int, sequence: int, description: str}}
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        self._initialize_repositories()
    
    def _initialize_repositories(self):
        """Initialize repositories with proper error handling"""
        try:
            from backend.db.repositories.project_repo import ProjectRepository
            self.project_repo = ProjectRepository(self.db_session)
            self.logger.info("✅ ProjectRepository initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize ProjectRepository: {e}")
            raise
    

    @error_decorator(return_none=False)
    def create_project(self, user_id: int, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create project with proper zones format handling and enforcing single project per name
        """
        #try:
        
        is_valid, errors = Validator.validate_project_data(project_data)
        if not is_valid:
            raise AppError(
                message="Project validation failed",
                code="VALIDATION_ERROR",
                details={'errors': errors}
            )
        self.logger.info(f"Creating project for user {user_id}: {project_data.get('name')}")

        # Validate required data
        if not project_data.get('name'):
            raise ValueError("Project name is required")
        
        # Validate zones format
        zones = project_data.get('zones', {})
        self._validate_zones_format(zones)

        # Prepare database payload
        db_payload = {
            'name': project_data['name'],
            'description': project_data.get('description', ''),
            'start_date': project_data.get('start_date'),
            'project_type': project_data.get('project_type', 'Commercial'),
            'owner': project_data.get('owner', ''),
            'location': project_data.get('location', ''),
            'zones': zones,
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now() 
        }

        # Advanced settings
        advanced_settings = project_data.get('advanced_settings', {})
        if advanced_settings:
            db_payload['constraints'] = advanced_settings

        # ✅ Use get_or_create_project to avoid duplicates
        project_db = self.project_repo.get_or_create_project(user_id, db_payload)

        frontend_data = self._db_to_frontend_format(project_db)
        self.logger.info(f"✅ Project ready for frontend: {project_db.name} (ID: {project_db.id})")
        return frontend_data

        #except Exception as e:
           # self.logger.error(f"❌ Error creating project: {e}")
            #raise
    
    def get_user_projects(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all projects for user in frontend-compatible format
        
        Args:
            user_id: Authenticated user ID
            
        Returns:
            List of project data for frontend
        """
        try:
            self.logger.info(f"Retrieving projects for user {user_id}")
            
            projects_db = self.project_repo.get_user_projects(user_id)
            frontend_projects = [self._db_to_frontend_format(project) for project in projects_db]
            
            self.logger.info(f"✅ Retrieved {len(frontend_projects)} projects for user {user_id}")
            return frontend_projects
            
        except Exception as e:
            self.logger.error(f"❌ Error retrieving user projects: {e}")
            return []
    
    @error_decorator(return_none=True)
    def get_project(self, user_id: int, project_id: int) -> Optional[Dict[str, Any]]:
        """Get project with authorization check"""
        project_db = self.project_repo.get_project(user_id, project_id)
        
        if not project_db:
            raise AppError(
                message="Project not found",
                code="NOT_FOUND",
                details={'project_id': project_id, 'user_id': user_id}
            )
        
        # Verify project belongs to user
        if project_db.user_id != user_id:
            raise AppError(
                message="Access denied to project",
                code="PERMISSION_DENIED",
                details={'project_id': project_id, 'user_id': user_id}
            )
        
        return self._db_to_frontend_format(project_db)
    
    def update_project(self, user_id: int, project_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update project with authorization check and zones format validation
        
        Args:
            user_id: Authenticated user ID (for authorization)
            project_id: Project ID to update
            update_data: Data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Updating project {project_id} for user {user_id}")
            
            # Verify user owns the project
            project_db = self.project_repo.get_project(user_id,project_id)
            if not project_db or project_db.user_id != user_id:
                self.logger.warning(f"❌ User {user_id} unauthorized to update project {project_id}")
                return False
            
            # Validate zones format if provided
            zones = update_data.get('zones') 
            if zones is not None:
                self._validate_zones_format(zones)
            
            # Prepare update payload
            update_payload = {
                'name': update_data.get('name', project_db.name),
                'description': update_data.get('description', project_db.description),
                'project_type':  update_data.get('project_type', project_db.project_type),
                'owner': update_data.get('owner', project_db.owner),
                'start_date' : update_data.get('start_date', project_db.start_date),
                'zones': update_data.get('zones', project_db.zones),
                'updated_at': datetime.now()
            }
            
            # Handle advanced settings
            advanced_settings = update_data.get('advanced_settings')
            if advanced_settings:
                update_payload['constraints'] = advanced_settings
            
            success = self.project_repo.update_project(user_id, project_id, update_payload)
            
            if success:
                self.logger.info(f"✅ Project {project_id} updated successfully")
            else:
                self.logger.error(f"❌ Failed to update project {project_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error updating project {project_id}: {e}")
            return False
    
    def delete_project(self, user_id: int, project_id: int) -> bool:
        """
        Soft delete project (archive it)
        
        Args:
            user_id: Authenticated user ID
            project_id: Project ID to archive
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify authorization
            project_db = self.project_repo.get_project(user_id,project_id)
            if not project_db or project_db.user_id != user_id:
                return False
            
            update_data = {
                'status': 'archived',
                'updated_at': datetime.now()
            }
            
            return self.project_repo.update_project(project_id, update_data)
            
        except Exception as e:
            self.logger.error(f"❌ Error deleting project {project_id}: {e}")
            return False
    
    def get_project_progress_summary(self,user_id, project_id: int) -> Dict[str, Any]:
        """
        Get comprehensive project progress summary
        
        Args:
            project_id: Project ID
            
        Returns:
            Progress summary data
        """
        try:
            # Use repository method if available
            if hasattr(self.project_repo, 'get_project_progress_summary'):
                summary = self.project_repo.get_project_progress_summary(project_id)
                if summary:
                    return summary
            
            # Fallback implementation
            project_db = self.project_repo.get_project(user_id,project_id)
            if not project_db:
                return {}
            
            return {
                'project_id': project_id,
                'project_name': project_db.name,
                'project_status': project_db.status,
                'start_date': project_db.start_date,
                'zone_count': len(project_db.zones) if project_db.zones else 0,
                'total_floors': self._calculate_total_floors(project_db.zones),
                'overall_completion': 0,
                'schedule_count': 0,
                'last_updated': project_db.updated_at.isoformat() if project_db.updated_at else None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting project progress summary: {e}")
            return {}
    
    def _db_to_frontend_format(self, project_db) -> Dict[str, Any]:
        """
        Convert database model to frontend-compatible format
        Preserves zones format: {zone_name: {max_floors: int, sequence: int, description: str}}
        
        Args:
            project_db: SQLAlchemy project model
            
        Returns:
            Frontend-compatible project data
        """
        try:
            # Extract basic info
            frontend_data = {
                'id': project_db.id,
                'name': project_db.name,
                'description': project_db.description or '',
                'start_date': project_db.start_date.isoformat() if project_db.start_date else None,
                'project_type': getattr(project_db, 'project_type', 'Commercial'),
                'owner': getattr(project_db, 'owner', ''),
                'location': getattr(project_db, 'location', ''),
                'status': project_db.status,
                'created_at': project_db.created_at.isoformat() if project_db.created_at else None,
                'updated_at': project_db.updated_at.isoformat() if project_db.updated_at else None
            }
            
            # Handle zones - ensure correct format
            zones = getattr(project_db, 'zones', {})
            if zones:
                # Ensure zones are in correct format
                validated_zones = {}
                for zone_name, zone_config in zones.items():
                    if isinstance(zone_config, dict):
                        # Already in correct format
                        validated_zones[zone_name] = {
                            'max_floors': zone_config.get('max_floors', 0),
                            'sequence': zone_config.get('sequence', 1),
                            'description': zone_config.get('description', '')
                        }
                    else:
                        # Convert simple format to complex format
                        validated_zones[zone_name] = {
                            'max_floors': zone_config,
                            'sequence': 1,
                            'description': ''
                        }
                frontend_data['zones'] = validated_zones
            else:
                frontend_data['zones'] = {}
            
            # Extract advanced settings from constraints
            constraints = getattr(project_db, 'constraints', {})
            if constraints:
                frontend_data['advanced_settings'] = constraints
            else:
                frontend_data['advanced_settings'] = {
                    'work_hours_per_day': 8,
                    'acceleration_factor': 1.0,
                    'risk_allowance': 0.1
                }
            
            return frontend_data
            
        except Exception as e:
            self.logger.error(f"❌ Error converting project to frontend format: {e}")
            # Return minimal safe data
            return {
                'id': getattr(project_db, 'id', None),
                'name': getattr(project_db, 'name', 'Unknown Project'),
                'zones': {},
                'advanced_settings': {},
                'status': 'error'
            }
    
    def _calculate_total_floors(self, zones: Dict) -> int:
        """Calculate total floors from zones configuration"""
        try:
            if not zones:
                return 0
            
            total = 0
            for zone_name, zone_config in zones.items():
                if isinstance(zone_config, dict):
                    total += zone_config.get('max_floors', 0)
                elif isinstance(zone_config, (int, float)):
                    total += int(zone_config)
            
            return total
        except Exception as e:
            self.logger.error(f"Error calculating total floors: {e}")
            return 0
    
    def _validate_zones_format(self, zones: Dict[str, Any]):
        """
        Validate zones format is correct: {zone_name: {max_floors: int, sequence: int, description: str}}
        
        Args:
            zones: Zones data to validate
            
        Raises:
            ValueError: If zones format is invalid
        """
        if not isinstance(zones, dict):
            raise ValueError("Zones must be a dictionary")
        
        for zone_name, zone_config in zones.items():
            if not isinstance(zone_name, str) or not zone_name.strip():
                raise ValueError(f"Invalid zone name: {zone_name}")
            
            if not isinstance(zone_config, dict):
                raise ValueError(f"Zone configuration for '{zone_name}' must be a dictionary")
            
            # Check required fields
            if 'max_floors' not in zone_config:
                raise ValueError(f"Zone '{zone_name}' missing 'max_floors' field")
            
            max_floors = zone_config['max_floors']
            if not isinstance(max_floors, (int, float)) or max_floors < 0:
                raise ValueError(f"Zone '{zone_name}' has invalid max_floors: {max_floors}")
    
    def validate_project_configuration(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Professional validation of project configuration
        
        Args:
            project_data: Project data to validate
            
        Returns:
            Validation results
        """
        errors = []
        warnings = []
        
        # Required fields validation
        if not project_data.get('name') or not project_data['name'].strip():
            errors.append("Project name is required")
        
        if not project_data.get('start_date'):
            errors.append("Project start date is required")
        
        # Zones validation
        zones = project_data.get('zones', {})
        if not zones:
            warnings.append("No zones configured - project scheduling will be limited")
        else:
            try:
                self._validate_zones_format(zones)
                
                # Additional business logic validation
                for zone_name, zone_config in zones.items():
                    max_floors = zone_config.get('max_floors', 0)
                    if not isinstance(max_floors, int) or max_floors < 1:
                        errors.append(f"Zone '{zone_name}': max_floors must be positive integer")
                    
                    sequence = zone_config.get('sequence', 1)
                    if not isinstance(sequence, int) or sequence < 1:
                        errors.append(f"Zone '{zone_name}': sequence must be positive integer")
                        
            except ValueError as e:
                errors.append(str(e))
        
        # Advanced settings validation
        advanced_settings = project_data.get('advanced_settings', {})
        work_hours = advanced_settings.get('work_hours_per_day', 8)
        if not isinstance(work_hours, (int, float)) or not (1 <= work_hours <= 24):
            errors.append("Work hours per day must be between 1 and 24")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'summary': {
                'has_basic_info': bool(project_data.get('name') and project_data.get('start_date')),
                'zone_count': len(zones),
                'total_floors': self._calculate_total_floors(zones),
                'has_advanced_settings': bool(advanced_settings)
            }
        }