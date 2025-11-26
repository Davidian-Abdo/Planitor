"""
PROFESSIONAL Resource Service - Workers & Equipment Management
UPDATED with proper template association handling and modification tracking
"""
import logging
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class ResourceService:
    """
    Professional service for resource operations (workers + equipment)
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        self._initialize_repositories()
    
    def _initialize_repositories(self):
        """Initialize repositories"""
        try:
            from backend.db.repositories.resource_repo import ResourceRepository
            self.resource_repo = ResourceRepository(self.db_session)
            self.logger.info("✅ ResourceRepository initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ ResourceRepository initialization failed: {e}")
            raise
    
    def get_user_resource_templates(self, user_id: int) -> List[Dict]:
        """Get user resource templates"""
        try:
            db_templates = self.resource_repo.get_user_resource_templates(user_id)
            domain_templates = [self._db_to_domain_resource_template(db_template) for db_template in db_templates]
            self.logger.info(f"✅ Retrieved {len(domain_templates)} resource templates for user {user_id}")
            return domain_templates
        except Exception as e:
            self.logger.error(f"❌ Error retrieving resource templates: {e}")
            return []
    
    def get_workers_by_template(self, template_id: int) -> List[Dict]:
        """Get workers by template ID"""
        try:
            db_workers = self.resource_repo.get_workers_by_template(template_id)
            return [self._db_to_domain_worker(w) for w in db_workers]
        except Exception as e:
            self.logger.error(f"Error getting workers by template: {e}")
            return []

    def get_equipment_by_template(self, template_id: int) -> List[Dict]:
        """Get equipment by template ID"""
        try:
            db_equipment = self.resource_repo.get_equipment_by_template(template_id)
            return [self._db_to_domain_equipment(e) for e in db_equipment]
        except Exception as e:
            self.logger.error(f"Error getting equipment by template: {e}")
            return []

    def get_user_workers(self, user_id: int, template_id: Optional[int] = None) -> List[Dict]:
        """Get user workers"""
        try:
            db_workers = self.resource_repo.get_user_workers(user_id, template_id)
            domain_workers = [self._db_to_domain_worker(db_worker) for db_worker in db_workers]
            self.logger.info(f"✅ Retrieved {len(domain_workers)} workers for user {user_id}")
            return domain_workers
        except Exception as e:
            self.logger.error(f"❌ Error retrieving workers: {e}")
            return []
    
    def get_user_equipment(self, user_id: int, template_id: Optional[int] = None) -> List[Dict]:
        """Get user equipment"""
        try:
            db_equipment = self.resource_repo.get_user_equipment(user_id, template_id)
            domain_equipment = [self._db_to_domain_equipment(db_equip) for db_equip in db_equipment]
            self.logger.info(f"✅ Retrieved {len(domain_equipment)} equipment for user {user_id}")
            return domain_equipment
        except Exception as e:
            self.logger.error(f"❌ Error retrieving equipment: {e}")
            return []
    
    def get_resource_counts(self, template_id: int) -> tuple[int, int]:
        """Get worker and equipment counts for a template"""
        try:
            workers = self.resource_repo.get_workers_by_template(template_id)
            equipment = self.resource_repo.get_equipment_by_template(template_id)
            return len(workers), len(equipment)
        except Exception as e:
            self.logger.error(f"Error getting resource counts: {e}")
            return 0, 0
    
    def create_resource_template(self, user_id: int, template_data: Dict) -> Optional[Dict]:
        """Create new resource template and return created template"""
        try:
            template_data['user_id'] = user_id
            db_template = self.resource_repo.create_resource_template(template_data)
            if db_template:
                domain_template = self._db_to_domain_resource_template(db_template)
                self.logger.info(f"✅ Created resource template: {template_data['name']}")
                return domain_template
            return None
        except Exception as e:
            self.logger.error(f"❌ Error creating resource template: {e}")
            return None
    
    def get_template_resources(self, template_id: int) -> Dict[str, List]:
        """Get all resources (workers + equipment) for a template"""
        try:
            workers = self.resource_repo.get_workers_by_template(template_id)
            equipment = self.resource_repo.get_equipment_by_template(template_id)
            
            return {
                'workers': [self._db_to_domain_worker(w) for w in workers],
                'equipment': [self._db_to_domain_equipment(e) for e in equipment]
            }
        except Exception as e:
            logger.error(f"Error getting template resources: {e}")
            return {'workers': [], 'equipment': []}
    
    def update_resource_template(self, template_id: int, updates: Dict) -> bool:
        """Update resource template"""
        try:
            success = self.resource_repo.update_resource_template(template_id, updates)
            if success:
                self.logger.info(f"✅ Updated resource template ID: {template_id}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error updating resource template: {e}")
            return False
    
    def create_worker(self, user_id: int, worker_data: Dict) -> Optional[Dict]:
        """Create new worker and return created worker"""
        try:
            worker_data['user_id'] = user_id
            
            # Generate code if not provided
            if not worker_data.get('code'):
                base_name = worker_data['name'][:3].upper()
                worker_data['code'] = f"WRK_{base_name}_{len(self.get_user_workers(user_id)) + 1:03d}"
            
            db_worker = self.resource_repo.create_worker(worker_data)
            if db_worker:
                domain_worker = self._db_to_domain_worker(db_worker)
                self.logger.info(f"✅ Created worker: {worker_data['name']}")
                return domain_worker
            return None
        except Exception as e:
            self.logger.error(f"❌ Error creating worker: {e}")
            return None
    
    def update_worker(self, user_id: int, worker_id: int, updates: Dict) -> Optional[Dict]:
        """Update worker and return updated worker"""
        try:
            db_worker = self.resource_repo.update_worker(worker_id, user_id, updates)
            if db_worker:
                domain_worker = self._db_to_domain_worker(db_worker)
                self.logger.info(f"✅ Updated worker ID: {worker_id}")
                return domain_worker
            return None
        except Exception as e:
            self.logger.error(f"❌ Error updating worker: {e}")
            return None

    def update_worker_with_template_check(self, user_id: int, worker_id: int, updates: Dict) -> Optional[Dict]:
        """Update worker and mark template as modified if it was default"""
        try:
            # First get the current worker to check template
            current_worker = self.resource_repo.get_worker_by_id(worker_id)
            if not current_worker:
                return None
            
            template_id = current_worker.template_id
            if template_id:
                # Check if template is default and mark it as modified
                self._mark_template_as_modified_if_default(template_id)
            
            # Now update the worker
            return self.update_worker(user_id, worker_id, updates)
            
        except Exception as e:
            self.logger.error(f"❌ Error updating worker with template check: {e}")
            return None
    
    def delete_worker(self, user_id: int, worker_id: int) -> bool:
        """Delete worker"""
        try:
            success = self.resource_repo.delete_worker(worker_id, user_id)
            if success:
                self.logger.info(f"✅ Deleted worker ID: {worker_id}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error deleting worker: {e}")
            return False
    
    def create_equipment(self, user_id: int, equipment_data: Dict) -> Optional[Dict]:
        """Create new equipment and return created equipment"""
        try:
            equipment_data['user_id'] = user_id
            
            # Generate code if not provided
            if not equipment_data.get('code'):
                base_name = equipment_data['name'][:3].upper()
                equipment_data['code'] = f"EQP_{base_name}_{len(self.get_user_equipment(user_id)) + 1:03d}"
            
            db_equipment = self.resource_repo.create_equipment(equipment_data)
            if db_equipment:
                domain_equipment = self._db_to_domain_equipment(db_equipment)
                self.logger.info(f"✅ Created equipment: {equipment_data['name']}")
                return domain_equipment
            return None
        except Exception as e:
            self.logger.error(f"❌ Error creating equipment: {e}")
            return None
    
    def update_equipment(self, user_id: int, equipment_id: int, updates: Dict) -> Optional[Dict]:
        """Update equipment and return updated equipment"""
        try:
            db_equipment = self.resource_repo.update_equipment(equipment_id, user_id, updates)
            if db_equipment:
                domain_equipment = self._db_to_domain_equipment(db_equipment)
                self.logger.info(f"✅ Updated equipment ID: {equipment_id}")
                return domain_equipment
            return None
        except Exception as e:
            self.logger.error(f"❌ Error updating equipment: {e}")
            return None

    def update_equipment_with_template_check(self, user_id: int, equipment_id: int, updates: Dict) -> Optional[Dict]:
        """Update equipment and mark template as modified if it was default"""
        try:
            # First get the current equipment to check template
            current_equipment = self.resource_repo.get_equipment_by_id(equipment_id)
            if not current_equipment:
                return None
            
            template_id = current_equipment.template_id
            if template_id:
                # Check if template is default and mark it as modified
                self._mark_template_as_modified_if_default(template_id)
            
            # Now update the equipment
            return self.update_equipment(user_id, equipment_id, updates)
            
        except Exception as e:
            self.logger.error(f"❌ Error updating equipment with template check: {e}")
            return None
    
    def delete_equipment(self, user_id: int, equipment_id: int) -> bool:
        """Delete equipment"""
        try:
            success = self.resource_repo.delete_equipment(equipment_id, user_id)
            if success:
                self.logger.info(f"✅ Deleted equipment ID: {equipment_id}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error deleting equipment: {e}")
            return False

    def _mark_template_as_modified_if_default(self, template_id: int):
        """Mark a template as modified (no longer default) if it was default"""
        try:
            template = self.resource_repo.get_template_by_id(template_id)
            if template and template.is_default:
                # Mark template as no longer default
                updates = {'is_default': False}
                success = self.resource_repo.update_resource_template(template_id, updates)
                if success:
                    self.logger.info(f"📝 Template {template_id} marked as modified (no longer default)")
                return success
            return False
        except Exception as e:
            self.logger.error(f"❌ Error marking template as modified: {e}")
            return False
    
    def load_default_resources(self, user_id: int) -> List[Dict]:
        """
        FIXED: Load default resources as user templates with proper template state management
        Returns newly created resources and handles template modification state
        """
        try:
            from backend.defaults.resources import workers, equipment
            
            created_resources = []
            
            # FIRST: Check for existing default templates
            existing_templates = self.get_user_resource_templates(user_id)
            default_template = None
            modified_default_templates = []
            
            # Separate default and modified default templates
            for template in existing_templates:
                if template.get('is_default') and 'Défaut' in template.get('name', ''):
                    default_template = template
                    self.logger.info(f"✅ Found active default template: {template['name']} (ID: {template['id']})")
                elif not template.get('is_default') and 'Défaut' in template.get('name', ''):
                    modified_default_templates.append(template)
                    self.logger.info(f"📝 Found modified default template: {template['name']} (ID: {template['id']})")
            
            # If no active default template exists, create one
            if not default_template:
                template_data = {
                    'name': 'Ressources par Défaut',
                    'description': 'Template de ressources par défaut pour la construction',
                    'user_id': user_id,
                    'category': 'Default',
                    'is_default': True
                }
                
                default_template = self.create_resource_template(user_id, template_data)
                if not default_template:
                    self.logger.error("❌ Failed to create default resource template")
                    return []
                
                self.logger.info(f"✅ Created new default resource template: {default_template['id']}")
            
            template_id = default_template['id']
            
            # Get existing resources for THIS template to avoid duplicates
            existing_workers = self.get_workers_by_template(template_id)
            existing_equipment = self.get_equipment_by_template(template_id)
            
            existing_worker_names = {w['name'] for w in existing_workers}
            existing_equipment_names = {e['name'] for e in existing_equipment}
            
            # Load default workers
            worker_count = 0
            for worker_name, worker_resource in workers.items():
                if worker_name not in existing_worker_names:
                    worker_code = f"WRK_{worker_name[:3].upper()}"
                    worker_data = {
                        'user_id': user_id,
                        'template_id': template_id,
                        'name': worker_name,
                        'code': worker_code,
                        'specialty': getattr(worker_resource, 'specialty', worker_name),
                        'category': 'Ouvrier',
                        'base_count': getattr(worker_resource, 'count', 1),
                        'hourly_rate': getattr(worker_resource, 'hourly_rate', 0.0),
                        'daily_rate': getattr(worker_resource, 'hourly_rate', 0.0) * 8,
                        'max_workers_per_crew': getattr(worker_resource, 'max_crews', {}).get('default', 1),
                        'base_productivity_rate': 1.0,
                        'productivity_unit': 'unités/jour',
                        'qualification_level': 'Qualifié',
                        'skills': getattr(worker_resource, 'skills', []),
                        'is_active': True
                    }
                    created_worker = self.create_worker(user_id, worker_data)
                    if created_worker:
                        created_resources.append(created_worker)
                        worker_count += 1
                        self.logger.info(f"✅ Created worker: {worker_name}")
            
            # Load default equipment
            equipment_count = 0
            for equip_name, equip_resource in equipment.items():
                if equip_name not in existing_equipment_names:
                    equipment_code = f"EQP_{equip_name[:3].upper()}"
                    equipment_data = {
                        'user_id': user_id,
                        'template_id': template_id,
                        'name': equip_name,
                        'code': equipment_code,
                        'type': getattr(equip_resource, 'type', 'EnginLourd'),
                        'category': 'EnginLourd',
                        'base_count': getattr(equip_resource, 'count', 1),
                        'hourly_rate': getattr(equip_resource, 'hourly_rate', 0.0),
                        'daily_rate': getattr(equip_resource, 'hourly_rate', 0.0) * 8,
                        'max_units_per_task': getattr(equip_resource, 'max_equipment', 1),
                        'base_productivity_rate': 1.0,
                        'productivity_unit': 'unités/jour',
                        'requires_operator': True,
                        'operator_type': 'ConducteurEngins',
                        'is_available': True,
                        'is_active': True
                    }
                    created_equipment = self.create_equipment(user_id, equipment_data)
                    if created_equipment:
                        created_resources.append(created_equipment)
                        equipment_count += 1
                        self.logger.info(f"✅ Created equipment: {equip_name}")
            
            self.logger.info(f"✅ Loaded {worker_count} workers and {equipment_count} equipment in default template {template_id}")
            
            # Return newly created resources or existing ones if no new ones
            if not created_resources and (existing_workers or existing_equipment):
                self.logger.info("✅ Default resources already exist, returning existing resources")
                return existing_workers + existing_equipment
            
            return created_resources
            
        except Exception as e:
            self.logger.error(f"❌ Error loading default resources: {e}")
            return []
    
    def export_resources_to_json(self) -> str:
        """Export resources to JSON format"""
        try:
            user_id = 1  # From session
            workers = self.get_user_workers(user_id)
            equipment = self.get_user_equipment(user_id)
            templates = self.get_user_resource_templates(user_id)
            
            export_data = {
                'resource_templates': templates,
                'workers': workers,
                'equipment': equipment,
                'export_version': '1.0'
            }
            
            import json
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error exporting resources to JSON: {e}")
            return "{}"
    
    def import_resources_from_json(self, uploaded_file) -> bool:
        """Import resources from JSON file"""
        try:
            import json
            resources_data = json.load(uploaded_file)
            user_id = 1  # From session
            
            success_count = 0
            
            # Import workers
            if 'workers' in resources_data:
                for worker_data in resources_data['workers']:
                    worker_data['user_id'] = user_id
                    if self.create_worker(user_id, worker_data):
                        success_count += 1
            
            # Import equipment
            if 'equipment' in resources_data:
                for equipment_data in resources_data['equipment']:
                    equipment_data['user_id'] = user_id
                    if self.create_equipment(user_id, equipment_data):
                        success_count += 1
            
            self.logger.info(f"✅ Imported {success_count} resources from JSON")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Error importing resources from JSON: {e}")
            return False
    
    def _db_to_domain_resource_template(self, db_template) -> Dict:
        """Convert DB model to domain resource template dictionary"""
        return {
            'id': db_template.id,
            'name': db_template.name,
            'description': db_template.description,
            'category': db_template.category,
            'version': db_template.version,
            'is_default': db_template.is_default,
            'is_shared': db_template.is_shared,
            'is_active': db_template.is_active,
            'created_at': db_template.created_at.isoformat() if db_template.created_at else None
        }
    
    def _db_to_domain_worker(self, db_worker) -> Dict:
        """Convert DB model to domain worker dictionary"""
        return {
            'id': db_worker.id,
            'user_id': db_worker.user_id,
            'template_id': db_worker.template_id,
            'name': db_worker.name,
            'code': db_worker.code,
            'specialty': db_worker.specialty,
            'category': db_worker.category,
            'base_count': db_worker.base_count,
            'hourly_rate': float(db_worker.hourly_rate),
            'daily_rate': float(db_worker.daily_rate),
            'max_workers_per_crew': db_worker.max_workers_per_crew,
            'base_productivity_rate': float(db_worker.base_productivity_rate),
            'productivity_unit': db_worker.productivity_unit,
            'qualification_level': db_worker.qualification_level,
            'skills': db_worker.skills or [],
            'required_certifications': db_worker.required_certifications or [],
            'is_active': db_worker.is_active,
            'description': db_worker.description,
            'created_at': db_worker.created_at.isoformat() if db_worker.created_at else None
        }
    
    def _db_to_domain_equipment(self, db_equipment) -> Dict:
        """Convert DB model to domain equipment dictionary"""
        return {
            'id': db_equipment.id,
            'user_id': db_equipment.user_id,
            'template_id': db_equipment.template_id,
            'name': db_equipment.name,
            'code': db_equipment.code,
            'type': db_equipment.type,
            'category': db_equipment.category,
            'model': db_equipment.model,
            'base_count': db_equipment.base_count,
            'hourly_rate': float(db_equipment.hourly_rate),
            'daily_rate': float(db_equipment.daily_rate),
            'capacity': db_equipment.capacity,
            'max_units_per_task': db_equipment.max_units_per_task,
            'base_productivity_rate': float(db_equipment.base_productivity_rate),
            'productivity_unit': db_equipment.productivity_unit,
            'requires_operator': db_equipment.requires_operator,
            'operator_type': db_equipment.operator_type,
            'is_available': db_equipment.is_available,
            'is_active': db_equipment.is_active,
            'description': db_equipment.description,
            'created_at': db_equipment.created_at.isoformat() if db_equipment.created_at else None
        }