"""
PROFESSIONAL Template Service - Template Association Management
Handles associations between resource templates and task templates
"""
import logging
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
import datetime

logger = logging.getLogger(__name__)

class TemplateService:
    """
    Professional service for template association operations
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        
    def validate_template_compatibility(self, resource_template: Dict, task_template: Dict) -> Dict[str, Any]:
        """Essential template compatibility validation"""
        try:
            issues = []
            warnings = []
            
            # 1. Check resource requirements
            resource_check = self._check_resource_requirements(task_template, resource_template)
            if not resource_check['met']:
                issues.extend(resource_check.get('issues', []))
            
            # 2. Check equipment requirements
            equipment_check = self._check_equipment_requirements(task_template, resource_template)
            if not equipment_check['met']:
                issues.extend(equipment_check.get('issues', []))
            
            return {
                'compatible': len(issues) == 0,
                'issues': issues,
                'warnings': warnings,
                'resource_check': resource_check,
                'equipment_check': equipment_check
            }
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                'compatible': False,
                'issues': [f"Erreur validation: {str(e)}"],
                'warnings': []
            }

    def _check_resource_requirements(self, task_template: Dict, resource_template: Dict) -> Dict[str, Any]:
        """Check if resource template has required workers"""
        from backend.db.repositories.resource_repo import ResourceRepository
        resource_repo = ResourceRepository(self.db_session)
        
        required_type = task_template.get('resource_type')
        if not required_type:
            return {'met': True, 'message': 'Aucun type spécifique requis'}
        
        workers = resource_repo.get_workers_by_template(resource_template['id'])
        worker_types = [w.specialty for w in workers]
        
        has_match = required_type in worker_types
        result = {
            'met': has_match,
            'required': required_type,
            'available': worker_types
        }
        
        if not has_match:
            result['issues'] = [f"Type ouvrier manquant: {required_type}"]
        
        return result

    def _check_equipment_requirements(self, task_template: Dict, resource_template: Dict) -> Dict[str, Any]:
        """Check if resource template has required equipment"""
        from backend.db.repositories.resource_repo import ResourceRepository
        resource_repo = ResourceRepository(self.db_session)
        
        required_equipment = task_template.get('min_equipment_needed', {})
        if not required_equipment:
            return {'met': True, 'message': 'Aucun équipement spécifique requis'}
        
        equipment = resource_repo.get_equipment_by_template(resource_template['id'])
        equipment_names = [e.name for e in equipment]
        
        missing = [name for name in required_equipment.keys() if name not in equipment_names]
        result = {
            'met': len(missing) == 0,
            'required': list(required_equipment.keys()),
            'available': equipment_names,
            'missing': missing
        }
        
        if missing:
            result['issues'] = [f"Équipements manquants: {', '.join(missing)}"]
        
        return result
    def get_available_resource_templates(self, user_id: int) -> List[Dict]:
        """Get available resource templates for user"""
        try:
            from backend.db.repositories.resource_repo import ResourceRepository
            resource_repo = ResourceRepository(self.db_session)
            
            db_templates = resource_repo.get_user_resource_templates(user_id)
            
            templates = []
            for template in db_templates:
                template_dict = {
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'version': template.version,
                    'is_default': template.is_default,
                    'is_shared': template.is_shared,
                    'is_active': template.is_active,
                    'created_at': template.created_at.isoformat() if template.created_at else None
                }
                
                # Get resource counts
                counts = resource_repo.count_template_resources(template.id)
                template_dict['worker_count'] = counts['workers']
                template_dict['equipment_count'] = counts['equipment']
                template_dict['total_resources'] = counts['total']
                
                templates.append(template_dict)
            
            self.logger.info(f"✅ Retrieved {len(templates)} resource templates for user {user_id}")
            return templates
            
        except Exception as e:
            self.logger.error(f"❌ Error getting resource templates: {e}")
            return []
    
    def get_template_associations(self, resource_template_id: int) -> List[Dict]:
        """Get task template associations for a resource template"""
        try:
            # In a real implementation, this would query an association table
            # For now, we'll return an empty list as placeholder
            associations = []
            
            self.logger.info(f"✅ Retrieved {len(associations)} associations for template {resource_template_id}")
            return associations
            
        except Exception as e:
            self.logger.error(f"❌ Error getting template associations: {e}")
            return []
    
    def associate_task_template(self, resource_template_id: int, task_template_id: str) -> bool:
        """Associate a task template with a resource template"""
        try:
            # In a real implementation, this would insert into an association table
            # For now, we'll log and return True as placeholder
            self.logger.info(f"✅ Associated resource template {resource_template_id} with task {task_template_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error associating templates: {e}")
            return False
    
    def remove_task_association(self, resource_template_id: int, task_template_id: str) -> bool:
        """Remove association between resource and task templates"""
        try:
            # In a real implementation, this would delete from an association table
            # For now, we'll log and return True as placeholder
            self.logger.info(f"✅ Removed association between resource template {resource_template_id} and task {task_template_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error removing association: {e}")
            return False
    
    def validate_task_template_dependencies(self, task_template: Dict, resource_template_id: int) -> Dict[str, Any]:
        """Validate if a task template's resource dependencies are satisfied by a resource template"""
        try:
            from backend.db.repositories.resource_repo import ResourceRepository
            resource_repo = ResourceRepository(self.db_session)
            
            missing_workers = []
            missing_equipment = []
            warnings = []
            
            # Get resources from the template
            workers = resource_repo.get_workers_by_template(resource_template_id)
            equipment = resource_repo.get_equipment_by_template(resource_template_id)
            
            # Check worker requirements
            required_worker_type = task_template.get('resource_type')
            if required_worker_type:
                worker_available = any(
                    w.specialty == required_worker_type or w.name == required_worker_type 
                    for w in workers
                )
                if not worker_available:
                    missing_workers.append(required_worker_type)
            
            # Check equipment requirements
            required_equipment = task_template.get('min_equipment_needed', {})
            for equip_name, quantity in required_equipment.items():
                equipment_available = any(
                    e.name == equip_name or e.code == equip_name 
                    for e in equipment
                )
                if not equipment_available:
                    missing_equipment.append(f"{equip_name} (x{quantity})")
            
            # Check if task has any resource dependencies at all
            if not required_worker_type and not required_equipment:
                warnings.append("Cette tâche n'a pas de dépendances de ressources spécifiées")
            
            return {
                'is_valid': len(missing_workers) == 0 and len(missing_equipment) == 0,
                'missing_workers': missing_workers,
                'missing_equipment': missing_equipment,
                'warnings': warnings,
                'resource_template_id': resource_template_id,
                'task_template_id': task_template.get('base_task_id')
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error validating task dependencies: {e}")
            return {
                'is_valid': False,
                'missing_workers': [],
                'missing_equipment': [],
                'warnings': [f"Erreur de validation: {str(e)}"],
                'resource_template_id': resource_template_id,
                'task_template_id': task_template.get('base_task_id')
            }
    
    def create_template_association_table(self) -> bool:
        """Create the template association table if it doesn't exist"""
        try:
            # This would typically create an association table in the database
            # For now, we'll just log and return True
            self.logger.info("✅ Template association table ready")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creating association table: {e}")
            return False
        

    def export_resource_templates(self, user_id: int) -> str:
        """
        Export resource templates to JSON format for download
        Includes templates, workers, and equipment
        """
        try:
            from backend.services.resource_service import ResourceService
            resource_service = ResourceService(self.db_session)
        
            # Get all resource data
            resource_templates = resource_service.get_user_resource_templates(user_id)
        
            export_data = {
                'export_type': 'resource_templates',
                'export_version': '1.0',
                'export_timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'resource_templates': resource_templates,
                'total_templates': len(resource_templates)
            }
        
            # Add workers and equipment for each template
            for template in resource_templates:
                template_id = template['id']
                workers = resource_service.get_workers_by_template(template_id)
                equipment = resource_service.get_equipment_by_template(template_id)
            
                template['workers'] = workers
                template['equipment'] = equipment
                template['worker_count'] = len(workers)
                template['equipment_count'] = len(equipment)
        
            import json
            return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        
        except Exception as e:
            self.logger.error(f"❌ Error exporting resource templates: {e}")
            return json.dumps({'error': str(e)})

    def import_resource_templates(self, user_id: int, uploaded_file) -> bool:
        """
        Import resource templates from JSON file
        """
        try:
            import json
            from backend.services.resource_service import ResourceService
            resource_service = ResourceService(self.db_session)
        
            # Parse uploaded file
            file_content = uploaded_file.getvalue().decode('utf-8')
            import_data = json.loads(file_content)
        
            # Validate export format
            if import_data.get('export_type') != 'resource_templates':
                raise ValueError("Invalid file format: Not a resource templates export")
        
            resource_templates = import_data.get('resource_templates', [])
            imported_count = 0
        
            for template_data in resource_templates:
                try:
                    # Create or update resource template
                    existing_templates = resource_service.get_user_resource_templates(user_id)
                    existing_template = next(
                        (t for t in existing_templates if t['name'] == template_data['name']), 
                         None
                    )
                
                    if existing_template:
                        # Update existing template
                        updates = {
                            'description': template_data.get('description', ''),
                            'category': template_data.get('category', 'Custom'),
                            'version': template_data.get('version', 1) + 1
                        }
                        success = resource_service.update_resource_template(existing_template['id'], updates)
                        template_id = existing_template['id']
                    else:
                        # Create new template
                        new_template_data = {
                        'name': template_data['name'],
                        'description': template_data.get('description', ''),
                        'category': template_data.get('category', 'Custom'),
                        'user_id': user_id,
                        'is_default': False,
                        'is_shared': template_data.get('is_shared', False)
                        }
                        new_template = resource_service.create_resource_template(user_id, new_template_data)
                        template_id = new_template['id'] if new_template else None
                
                    if template_id:
                        # Import workers
                        workers = template_data.get('workers', [])
                        for worker_data in workers:
                            worker_data['user_id'] = user_id
                            worker_data['template_id'] = template_id
                            resource_service.create_worker(user_id, worker_data)
                      
                        # Import equipment
                        equipment_list = template_data.get('equipment', [])
                        for equipment_data in equipment_list:
                            equipment_data['user_id'] = user_id
                            equipment_data['template_id'] = template_id
                            resource_service.create_equipment(user_id, equipment_data)
                    
                        imported_count += 1
                    
                except Exception as template_error:
                    self.logger.error(f"Error importing template {template_data.get('name')}: {template_error}")
                    continue
        
            self.logger.info(f"✅ Imported {imported_count} resource templates for user {user_id}")
            return imported_count > 0
        
        except Exception as e:
            self.logger.error(f"❌ Error importing resource templates: {e}")
            return False

    def export_task_templates(self, user_id: int) -> str:
        """
        Export task templates to JSON format for download
        """
        try:
            from backend.services.user_task_service import UserTaskService
            task_service = UserTaskService(self.db_session)
        
            # Get all task templates
            task_templates = task_service.get_user_task_templates(user_id)
        
            export_data = {
            'export_type': 'task_templates',
            'export_version': '1.0',
            'export_timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'task_templates': task_templates,
            'total_tasks': len(task_templates)
            }
        
            import json
            return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        
        except Exception as e:
            self.logger.error(f"❌ Error exporting task templates: {e}")
            return json.dumps({'error': str(e)})

    def import_task_templates(self, user_id: int, uploaded_file) -> bool:
        """
        Import task templates from JSON file
        """
        try:
            import json
            from backend.services.user_task_service import UserTaskService
            task_service = UserTaskService(self.db_session)
        
            # Parse uploaded file
            file_content = uploaded_file.getvalue().decode('utf-8')
            import_data = json.loads(file_content)
        
            # Validate export format
            if import_data.get('export_type') != 'task_templates':
                raise ValueError("Invalid file format: Not a task templates export")
        
            task_templates = import_data.get('task_templates', [])
            imported_count = 0
        
            for task_data in task_templates:
                try:
                    # Check if task already exists
                    existing_tasks = task_service.get_user_task_templates(user_id)
                    existing_task = next(
                        (t for t in existing_tasks if t.get('base_task_id') == task_data.get('base_task_id')), 
                        None
                    )
                 
                    if existing_task:
                        # Update existing task
                        updates = {
                            'name': task_data.get('name'),
                            'discipline': task_data.get('discipline'),
                            'base_duration': task_data.get('base_duration'),
                            'duration_calculation_method': task_data.get('duration_calculation_method', 'fixed_duration'),
                            'min_crews_needed': task_data.get('min_crews_needed', 1),
                            'min_equipment_needed': task_data.get('min_equipment_needed', {}),
                            'included': task_data.get('included', True)
                        }
                        updated_task = task_service.update_custom_task(user_id, existing_task['base_task_id'], updates)
                        if updated_task:
                            imported_count += 1
                    else:
                        # Create new task
                        task_data['user_id'] = user_id
                        new_task = task_service.create_custom_task(user_id, task_data)
                        if new_task:
                            imported_count += 1
                        
                except Exception as task_error:
                    self.logger.error(f"Error importing task {task_data.get('name')}: {task_error}")
                    continue
        
            self.logger.info(f"✅ Imported {imported_count} task templates for user {user_id}")
            return imported_count > 0
        
        except Exception as e:
            self.logger.error(f"❌ Error importing task templates: {e}")
            return False

        