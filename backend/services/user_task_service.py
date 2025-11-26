"""
PROFESSIONAL User Task Service - UPDATED with duration calculation methods
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
logger = logging.getLogger(__name__)

class UserTaskService:
    """
    Professional service for user task operations with duration methods
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        self._initialize_repositories()
    
    def _initialize_repositories(self):
        """Initialize repositories"""
        try:
            from backend.db.repositories.task_repo import TaskRepository
            self.task_repo = TaskRepository(self.db_session)
            self.logger.info("✅ TaskRepository initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ TaskRepository initialization failed: {e}")
            raise
    
    def get_user_task_templates(self, user_id: int, project_id: Optional[int] = None) -> List[Dict]:
        """
        Get user task templates for frontend display with duration methods
        """
        try:  
            db_templates = self.task_repo.get_user_task_templates(user_id, project_id)
            domain_tasks = [self._db_to_domain_task(db_template) for db_template in db_templates]
            self.logger.info(f"✅ Retrieved {len(domain_tasks)} task templates for user {user_id}")
            return domain_tasks
        except Exception as e:
            self.logger.error(f"❌ Error retrieving task templates: {e}")
            return []
    
    def get_task_template_groups(self, user_id: int) -> List[Dict]:
        """Get task templates grouped by template_name"""
        try:
            tasks = self.get_user_task_templates(user_id)
            template_groups = {}
        
            for task in tasks:
                template_name = task.get('template_name', 'Default Template')
                if template_name not in template_groups:
                    template_groups[template_name] = {
                    'template_name': template_name,
                    'tasks': [],
                    'task_count': 0,
                    'disciplines': set(),
                    'created_at': task.get('created_at')
                    }
            
                template_groups[template_name]['tasks'].append(task)
                template_groups[template_name]['task_count'] += 1
                template_groups[template_name]['disciplines'].add(task.get('discipline', 'Non spécifié'))
        
            return list(template_groups.values())
        
        except Exception as e:
            self.logger.error(f"Error getting task template groups: {e}")
            return []
    def load_default_tasks(self,user_id: int) -> List[Dict]:
        """
        Load default tasks as user templates with duration methods
        """
        try:
            from backend.defaults.TASKS import BASE_TASKS
            
            created_tasks = [] 
            for discipline, task_list in BASE_TASKS.items(): 
                for base_task in task_list:
                    template_data = {
                    'user_id': user_id,
                    'base_task_id': getattr(base_task, 'id', 'None'),
                    'name': getattr(base_task, 'name', 'Un named'),
                    'discipline': getattr(base_task, 'discipline', 'General'),
                    'sub_discipline': getattr(base_task, 'sub_discipline', 'General'),
                    'resource_type': getattr(base_task, 'resource_type', 'worker'),
                    'task_type': getattr(base_task, 'task_type', 'worker'),
                    'base_duration': getattr(base_task, 'base_duration', 1),
                    'unit_duration': getattr(base_task, 'unit_duration', 1),
                    'duration_calculation_method': getattr(base_task, 'duration_calculation_method', 'fixed_duration'),
                    'min_crews_needed': getattr(base_task, 'min_crews_needed', 1),
                    'min_equipment_needed': getattr(base_task, 'min_equipment_needed', {}),
                    'predecessors': getattr(base_task, 'predecessors', []),
                    'repeat_on_floor': getattr(base_task, 'repeat_on_floor', True),
                    'delay': getattr(base_task, 'delay', 0),
                    'weather_sensitive': getattr(base_task, 'weather_sensitive', False),
                    'quality_gate': getattr(base_task, 'quality_gate', False),
                    'included': getattr(base_task, 'included', True)
                        }
                
                    db_template = self.task_repo.create_user_task_template(template_data)
                    if db_template:
                        domain_task = self._db_to_domain_task(db_template)
                        created_tasks.append(domain_task)
                
            self.logger.info(f"✅ Loaded {len(created_tasks)} default tasks")
            return created_tasks
            
        except Exception as e:
            self.logger.error(f"❌ Error loading default tasks: {e}")
            return []
    
    def update_custom_task(self, user_id: int, task_id: int, updates: Dict) -> Optional[Dict]:
        """Update custom task template with duration method support"""
        try:
            # Validate duration method configuration
            validation_result = self._validate_duration_configuration(updates)
            if not validation_result['is_valid']:
                self.logger.error(f"❌ Invalid duration configuration: {validation_result['errors']}")
                return None
            
            db_template = self.task_repo.update_user_task_template(user_id, task_id, updates)
            
            if db_template:
                self.logger.info(f"✅ Updated task {task_id} with duration method: {updates.get('duration_calculation_method')}")
                return self._db_to_domain_task(db_template)
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error updating custom task: {e}")
            return None
    
    def _validate_duration_configuration(self, updates: Dict) -> Dict[str, Any]:
        """Validate duration calculation method configuration"""
        errors = []
        
        method = updates.get('duration_calculation_method', 'fixed_duration')
        
        if method == 'fixed_duration':
            if 'base_duration' not in updates or updates['base_duration'] <= 0:
                errors.append("La durée fixe doit être supérieure à 0")
                
        elif method == 'quantity_based':
            if 'unit_duration' not in updates or updates['unit_duration'] <= 0:
                errors.append("La durée unitaire doit être supérieure à 0")
        
        # resource_calculation doesn't need specific validation
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _db_to_domain_task(self, db_template) -> Dict:
        """Convert DB model to domain task dictionary with duration methods"""
        return {
            'base_task_id': db_template.base_task_id,
            'name': db_template.name,
            'discipline': db_template.discipline,
            'sub_discipline': db_template.sub_discipline,
            'resource_type': db_template.resource_type,
            'task_type': db_template.task_type,
            'base_duration': db_template.base_duration,
            'unit_duration': getattr(db_template, 'unit_duration', 0),
            'duration_calculation_method': getattr(db_template, 'duration_calculation_method', 'fixed_duration'),
            'min_crews_needed': db_template.min_crews_needed,
            'min_equipment_needed': db_template.min_equipment_needed or {},
            'predecessors': db_template.predecessors or [],
            'repeat_on_floor': db_template.repeat_on_floor,
            'delay': db_template.delay,
            'weather_sensitive': db_template.weather_sensitive,
            'quality_gate': db_template.quality_gate,
            'included': db_template.included,
            'created_at': db_template.created_at.isoformat() if db_template.created_at else None
        }
    
    # Keep existing methods for compatibility
    def import_tasks_from_json(self, uploaded_file) -> bool:
        """Import tasks from JSON file"""
        try:
            import json
            tasks_data = json.load(uploaded_file)
            user_id = 1  # From session
            
            success_count = 0
            for task_data in tasks_data:
                task_data['user_id'] = user_id
                # Ensure duration method is set
                if 'duration_calculation_method' not in task_data:
                    task_data['duration_calculation_method'] = 'fixed_duration'
                if self.task_repo.create_user_task_template(task_data):
                    success_count += 1
            
            self.logger.info(f"✅ Imported {success_count} tasks from JSON")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Error importing tasks from JSON: {e}")
            return False
    
    def export_tasks_to_json(self) -> str:
        """Export tasks to JSON format"""
        try:
            user_id = 1  # From session
            db_templates = self.task_repo.get_user_task_templates(user_id)
            
            tasks_data = []
            for db_template in db_templates:
                task_dict = {
                    'id': db_template.base_task_id,
                    'name': db_template.name,
                    'discipline': db_template.discipline,
                    'sub_discipline': db_template.sub_discipline,
                    'resource_type': db_template.resource_type,
                    'task_type': db_template.task_type,
                    'base_duration': db_template.base_duration,
                    'unit_duration': getattr(db_template, 'unit_duration', 0),
                    'duration_calculation_method': getattr(db_template, 'duration_calculation_method', 'fixed_duration'),
                    'min_crews_needed': db_template.min_crews_needed,
                    'min_equipment_needed': db_template.min_equipment_needed,
                    'predecessors': db_template.predecessors,
                    'repeat_on_floor': db_template.repeat_on_floor,
                    'delay': db_template.delay,
                    'weather_sensitive': db_template.weather_sensitive,
                    'quality_gate': db_template.quality_gate,
                    'included': db_template.included
                }
                tasks_data.append(task_dict)
            
            import json
            return json.dumps(tasks_data, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error exporting tasks to JSON: {e}")
            return "[]"
        



        # Add this method to UserTaskService class
    def create_custom_task(self, user_id: int, task_data: Dict) -> Optional[Dict]:
        """Create a new custom task template"""
        try:
            # Ensure required fields
            task_data['user_id'] = user_id
            if 'duration_calculation_method' not in task_data:
                task_data['duration_calculation_method'] = 'fixed_duration'
        
            db_template = self.task_repo.create_user_task_template(task_data)
        
            if db_template:
                self.logger.info(f"✅ Created custom task: {task_data.get('base_task_id')}")
                return self._db_to_domain_task(db_template)
            return None
        
        except Exception as e:
            self.logger.error(f"❌ Error creating custom task: {e}")
            return None
        
    def delete_custom_task(self, user_id: int, task_id: int) -> bool:
        """Delete custom task template"""
        try:
            return self.task_repo.delete_user_task_template(user_id, task_id)
        except Exception as e:
            self.logger.error(f"❌ Error deleting custom task: {e}")
            return False