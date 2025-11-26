"""
PROFESSIONAL Project Repository - PRODUCTION READY
Enhanced with proper transaction handling and zones format support
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from backend.models.db_models import ProjectDB, ScheduleDB

logger = logging.getLogger(__name__)

class ProjectRepository: 
    """Professional project data repository with enhanced error handling"""
    
    def __init__(self, session: Session):
        self.session = session
        self.logger = logger
    
    def get_user_projects(self, user_id: int, include_archived: bool = False) -> List[ProjectDB]:
        """
        Get all projects for a user with proper error handling
        
        Args:
            user_id: User ID to filter projects
            include_archived: Whether to include archived projects
            
        Returns:
            List of ProjectDB objects
        """
        try:
            self.logger.debug(f"Retrieving projects for user {user_id}")
            
            query = self.session.query(ProjectDB).filter(ProjectDB.user_id == user_id)
            
            if not include_archived:
                query = query.filter(ProjectDB.status != 'archived')
            
            projects = query.order_by(desc(ProjectDB.updated_at)).all()
            
            self.logger.info(f"✅ Retrieved {len(projects)} projects for user {user_id}")
            return projects
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get user projects for user {user_id}: {e}")
            return []
    
    def get_project(self, user_id: int, project_id: int) -> Optional[ProjectDB]:
        """
        Get a specific project by ID for a given user with schedules and proper error handling.
    
        Args:
        user_id: ID of the authenticated user
        project_id: Project ID to retrieve
        
        Returns:
        ProjectDB object or None if not found or not authorized
        """
        try:
            self.logger.debug(f"Retrieving project {project_id} for user {user_id}")
        
            project = self.session.query(ProjectDB).options(
                joinedload(ProjectDB.schedules)
            ).filter(
                ProjectDB.id == project_id,
                ProjectDB.user_id == user_id
            ).first()
        
            if project:
                self.logger.debug(f"✅ Retrieved project {project_id} for user {user_id}: {project.name}")
            else:
                self.logger.warning(f"⚠️ Project {project_id} not found or unauthorized for user {user_id}")
            
            return project    
        except Exception as e:
            self.logger.error(f"❌ Failed to get project {project_id} for user {user_id}: {e}")
            return None
    
    def create_project(self, project_data: Dict[str, Any]) -> Optional[ProjectDB]:
        """
        Create new project with proper error handling and logging
        
        Args:
            project_data: Dictionary containing project attributes
            
        Returns:
            Created ProjectDB object or None if failed
        """
        try:
            self.logger.info(f"Creating project: {project_data.get('name')}")
            
            # Validate required fields
            if not project_data.get('name'):
                raise ValueError("Project name is required")
            
            # Create project instance
            project = ProjectDB(**project_data)
            
            self.session.add(project)
            #self.session.commit() 
            self.session.flush()

            self.logger.info(f"✅ Project created successfully: {project.name} (ID: {project.id})")
            return project
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create project '{project_data.get('name')}': {e}")
            #self.session.rollback()
            return None
    
    def update_project(self,user_id, project_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update project with proper error handling and validation
        
        Args:
            project_id: Project ID to update
            update_data: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Updating project {project_id}")
            
            # Verify project exists
            project = self.get_project(user_id,project_id)
            if not project:
                self.logger.error(f"❌ Project {project_id} not found for update")
                return False
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(project, key):
                    setattr(project, key, value)
                    self.logger.debug(f"Updated field {key} for project {project_id}")
                else:
                    self.logger.warning(f"⚠️ Field {key} does not exist on ProjectDB, skipping")
            
            #self.session.commit()  # commit in the same session
            self.session.flush()
            self.logger.info(f"✅ Project {project_id} updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update project {project_id}: {e}")
            #self.session.rollback()
            return False
    def get_or_create_project(self, user_id: int, project_data: Dict[str, Any]) -> ProjectDB:
        """
        Get existing project by name for user, or create a new one.
        Enforces the rule: One project per name per user.
        """
        try:
            project = self.session.query(ProjectDB).filter_by(
                user_id=user_id,
                name=project_data.get("name"),
                status="active"
            ).first()
        
            if project:
                self.logger.info(f"✅ Project already exists: {project.name} (ID: {project.id})")
                return project
        
            return self.create_project({**project_data, "user_id": user_id})
    
        except Exception as e:
            self.logger.error(f"❌ Failed in get_or_create_project: {e}")
            self.session.rollback()
            return None  # ✅ Return None instead of re-raising to handle gracefully
    def delete_project(self, user_id,project_id: int) -> bool:
        """
        Hard delete project (use with caution)
        
        Args:
            project_id: Project ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.warning(f"🚨 Hard deleting project {project_id}")
            
            project = self.get_project(user_id,project_id)
            if not project:
                self.logger.error(f"❌ Project {project_id} not found for deletion")
                return False
            
            self.session.delete(project)
            self.session.flush()
            
            self.logger.info(f"✅ Project {project_id} deleted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete project {project_id}: {e}")
            self.session.rollback()
            return False
    
    def get_project_progress_summary(self,user_id, project_id: int) -> Dict[str, Any]:
        """
        Get comprehensive progress summary for a project
        
        Args:
            project_id: Project ID to get summary for
            
        Returns:
            Dictionary with progress metrics
        """
        try:
            self.logger.debug(f"Generating progress summary for project {project_id}")
            
            project = self.get_project(user_id,project_id)
            if not project:
                self.logger.warning(f"⚠️ Project {project_id} not found for progress summary")
                return {}
            
            # Get schedules for this project
            schedules = self.session.query(ScheduleDB).filter(
                ScheduleDB.project_id == project_id
            ).all()
            
            # Calculate progress metrics
            total_tasks = 0
            completed_tasks = 0
            in_progress_tasks = 0
            delayed_tasks = 0
            total_completion = 0
            
            for schedule in schedules:
                for task in schedule.tasks:
                    total_tasks += 1
                    total_completion += task.completion_percentage
                    
                    if task.status == 'completed':
                        completed_tasks += 1
                    elif task.status == 'in_progress':
                        in_progress_tasks += 1
                    elif task.status == 'delayed':
                        delayed_tasks += 1
            
            overall_completion = total_completion / total_tasks if total_tasks > 0 else 0
            
            summary = {
                'project_name': project.name,
                'project_status': project.status,
                'start_date': project.start_date,
                'target_end_date': project.target_end_date,
                'schedule_count': len(schedules),
                'total_tasks': total_tasks,
                'overall_completion': round(overall_completion, 2),
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'delayed_tasks': delayed_tasks,
                'last_schedule_date': max([s.generated_at for s in schedules]) if schedules else None,
                'zone_count': len(project.zones) if project.zones else 0,
                'total_floors': self._calculate_total_floors(project.zones)
            }
            
            self.logger.debug(f"✅ Progress summary generated for project {project_id}")
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get project progress summary for {project_id}: {e}")
            return {}
    
    def _calculate_total_floors(self, zones: Dict) -> int:
        """
        Calculate total floors from zones configuration
        
        Args:
            zones: Zones dictionary
            
        Returns:
            Total number of floors
        """
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
    
    def project_exists(self, user_id: int, project_name: str) -> bool:
        """
        Check if a project with the same name exists for the user
        
        Args:
            user_id: User ID to check
            project_name: Project name to check
            
        Returns:
            True if project exists, False otherwise
        """
        try:
            count = self.session.query(ProjectDB).filter(
                ProjectDB.user_id == user_id,
                ProjectDB.name == project_name,
                ProjectDB.status != 'archived'
            ).count()
            
            return count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Failed to check project existence: {e}")
            return False
    
    def get_recent_projects(self, user_id: int, limit: int = 5) -> List[ProjectDB]:
        """
        Get most recently updated projects for a user
        
        Args:
            user_id: User ID to filter projects
            limit: Maximum number of projects to return
            
        Returns:
            List of recent ProjectDB objects
        """
        try:
            return self.session.query(ProjectDB).filter(
                ProjectDB.user_id == user_id,
                ProjectDB.status != 'archived'
            ).order_by(
                desc(ProjectDB.updated_at)
            ).limit(limit).all()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get recent projects for user {user_id}: {e}")
            return []