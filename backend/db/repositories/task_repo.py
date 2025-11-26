"""
Professional Task Repository for CRUD operations
UPDATED with duration calculation methods support
"""
import logging
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.models.db_models import UserTaskTemplateDB
from backend.models.domain_models import BaseTask, TaskType

logger = logging.getLogger(__name__)

class TaskRepository:
    """
    Professional repository for task template operations with duration methods
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
    
    def get_user_task_templates(self, user_id: int, project_id: Optional[int] = None) -> List[UserTaskTemplateDB]:
        """
        Get all task templates for a user with duration methods
        """
        try:
            query = self.db_session.query(UserTaskTemplateDB).filter(
                UserTaskTemplateDB.user_id == user_id,
                UserTaskTemplateDB.is_active == True
            )
            
            if project_id:
                # If you add project-specific templates later
                pass
                
            templates = query.order_by(UserTaskTemplateDB.discipline, UserTaskTemplateDB.name).all()
            self.logger.info(f"Retrieved {len(templates)} task templates for user {user_id}")
            return templates
            
        except Exception as e:
            self.logger.error(f"Error getting user task templates: {e}")
            return []
    
    def create_user_task_template(self, task_data: Dict[str, Any]) -> Optional[UserTaskTemplateDB]:
        """
        Create a new user task template with duration method support
        """
        try:
            # Check if template already exists for this user and base_task_id
            existing = self.db_session.query(UserTaskTemplateDB).filter(
                UserTaskTemplateDB.user_id == task_data['user_id'],
                UserTaskTemplateDB.base_task_id == task_data['base_task_id']
            ).first()
            
            # Set default duration method if not provided
            if 'duration_calculation_method' not in task_data:
                task_data['duration_calculation_method'] = 'fixed_duration'
            
            if existing:
                # Update existing template
                for key, value in task_data.items():
                    if hasattr(existing, key) and key not in ['id', 'created_at']:
                        setattr(existing, key, value)

                self.logger.info(f"Updated existing task template: {task_data['base_task_id']}")
                return existing
            else:
                # Create new template
                db_template = UserTaskTemplateDB(**task_data)
                self.db_session.add(db_template)
                self.db_session.flush()
                self.logger.info(f"Created new task template: {task_data['base_task_id']}")
                return db_template
                
        except Exception as e:
   
            self.logger.error(f"Error creating task template: {e}")
            return None
    
    def update_user_task_template(self, user_id: int, task_id: int, updates: Dict[str, Any]) -> Optional[UserTaskTemplateDB]:
        """
        Update a user task template with duration method support
        """
        try:
            db_template = self.db_session.query(UserTaskTemplateDB).filter(
                UserTaskTemplateDB.id == task_id,
                UserTaskTemplateDB.user_id == user_id
            ).first()
            
            if db_template:
                for key, value in updates.items():
                    if hasattr(db_template, key) and key not in ['id', 'user_id', 'created_at']:
                        setattr(db_template, key, value)
                self.logger.info(f"Updated task template {task_id} with duration method: {updates.get('duration_calculation_method')}")
                return db_template
            else:
                self.logger.warning(f"Task template {task_id} not found for user {user_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error updating task template: {e}")
            return None
    
    # Keep existing methods for compatibility
    def get_user_task_templates_as_base_tasks(self, user_id: int, project_id: Optional[int] = None) -> Dict[str, BaseTask]:
        """
        CRITICAL: Convert user task templates to BaseTask format for the scheduler
        Now includes duration calculation methods
        """
        try:
            db_templates = self.get_user_task_templates(user_id, project_id)
            base_tasks = {}
            
            for db_template in db_templates:
                base_task_id = db_template.base_task_id
                
                # Create BaseTask object from user template with duration methods
                base_task = BaseTask(
                    id=base_task_id,
                    name=db_template.name,
                    discipline=db_template.discipline,
                    sub_discipline=db_template.sub_discipline,
                    resource_type=db_template.resource_type,
                    task_type=TaskType(db_template.task_type.upper()) if isinstance(db_template.task_type, str) else db_template.task_type,
                    base_duration=db_template.base_duration,
                    unit_duration=getattr(db_template, 'unit_duration', 0),
                    duration_calculation_method=getattr(db_template, 'duration_calculation_method', 'fixed_duration'),
                    min_crews_needed=db_template.min_crews_needed,
                    min_equipment_needed=db_template.min_equipment_needed or {},
                    predecessors=db_template.predecessors or [],
                    repeat_on_floor=db_template.repeat_on_floor,
                    delay=db_template.delay,
                    weather_sensitive=db_template.weather_sensitive,
                    quality_gate=db_template.quality_gate,
                    included=db_template.included
                )
                
                base_tasks[base_task_id] = base_task
            
            self.logger.info(f"Converted {len(base_tasks)} user templates to BaseTask format with duration methods")
            return base_tasks
            
        except Exception as e:
            self.logger.error(f"Error converting user templates to BaseTask: {e}")
            return {}
    
    def delete_user_task_template(self, user_id: int, task_id: int) -> bool:
        """
        Soft delete a user task template
        """
        try:
            db_template = self.db_session.query(UserTaskTemplateDB).filter(
                UserTaskTemplateDB.id == task_id,
                UserTaskTemplateDB.user_id == user_id
            ).first()
            
            if db_template:
                db_template.is_active = False

                self.logger.info(f"Soft deleted task template {task_id}")
                return True
            else:
                self.logger.warning(f"Task template {task_id} not found for user {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting task template: {e}")
            return False
