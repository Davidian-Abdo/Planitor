"""
PROFESSIONAL Resource Repository - UPDATED with Resource Template Support
Enhanced for unified resource management with proper template associations
"""
import logging
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.models.db_models import ResourceTemplateDB, WorkerResourceDB, EquipmentResourceDB

logger = logging.getLogger(__name__)

class ResourceRepository:
    """
    UPDATED Professional repository for resource operations with template support
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
    
    # RESOURCE TEMPLATE METHODS
    def get_user_resource_templates(self, user_id: int) -> List[ResourceTemplateDB]:
        """Get all resource templates for a user"""
        try:
            templates = self.db_session.query(ResourceTemplateDB).filter(
                ResourceTemplateDB.user_id == user_id,
                ResourceTemplateDB.is_active == True
            ).order_by(ResourceTemplateDB.name).all()
            
            self.logger.info(f"✅ Retrieved {len(templates)} resource templates for user {user_id}")
            return templates
            
        except Exception as e:
            self.logger.error(f"❌ Error getting user resource templates: {e}")
            return []
    
    def create_resource_template(self, template_data: Dict[str, Any]) -> Optional[ResourceTemplateDB]:
        """Create a new resource template - NO COMMIT"""
        try:
            # Check if template already exists for this user and name
            existing = self.db_session.query(ResourceTemplateDB).filter(
                ResourceTemplateDB.user_id == template_data['user_id'],
                ResourceTemplateDB.name == template_data['name']
            ).first()
            
            if existing:
                self.logger.warning(f"⚠️ Resource template already exists: {template_data['name']}")
                return existing
            
            db_template = ResourceTemplateDB(**template_data)
            self.db_session.add(db_template)
            self.db_session.flush()
            self.logger.info(f"✅ Created new resource template: {template_data['name']}")
            return db_template
            
        except Exception as e:
            self.logger.error(f"❌ Error creating resource template: {e}")
            return None
    
    def update_resource_template(self, template_id: int, updates: Dict[str, Any]) -> bool:
        """Update a resource template by ID - NO COMMIT"""
        try:
            db_template = self.db_session.query(ResourceTemplateDB).filter(
                ResourceTemplateDB.id == template_id
            ).first()
            
            if db_template:
                for key, value in updates.items():
                    if hasattr(db_template, key) and key not in ['id', 'user_id', 'created_at']:
                        setattr(db_template, key, value)
                self.db_session.flush()
                self.logger.info(f"✅ Updated resource template ID: {template_id}")
                return True
            else:
                self.logger.warning(f"⚠️ Resource template ID {template_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error updating resource template: {e}")
            return False
    
    def get_workers_by_template(self, template_id: int) -> List[WorkerResourceDB]:
        """Get all workers for a specific template"""
        try:
            workers = self.db_session.query(WorkerResourceDB).filter(
                WorkerResourceDB.template_id == template_id,
                WorkerResourceDB.is_active == True
            ).order_by(WorkerResourceDB.name).all()
            
            self.logger.info(f"✅ Retrieved {len(workers)} workers for template {template_id}")
            return workers
            
        except Exception as e:
            self.logger.error(f"❌ Error getting workers by template: {e}")
            return []
    
    def get_equipment_by_template(self, template_id: int) -> List[EquipmentResourceDB]:
        """Get all equipment for a specific template"""
        try:
            equipment = self.db_session.query(EquipmentResourceDB).filter(
                EquipmentResourceDB.template_id == template_id,
                EquipmentResourceDB.is_active == True
            ).order_by(EquipmentResourceDB.name).all()
            
            self.logger.info(f"✅ Retrieved {len(equipment)} equipment for template {template_id}")
            return equipment
            
        except Exception as e:
            self.logger.error(f"❌ Error getting equipment by template: {e}")
            return []
    
    # WORKER METHODS
    def get_user_workers(self, user_id: int, template_id: Optional[int] = None) -> List[WorkerResourceDB]:
        """Get all workers for a user"""
        try:
            query = self.db_session.query(WorkerResourceDB).filter(
                WorkerResourceDB.user_id == user_id,
                WorkerResourceDB.is_active == True
            )
            
            if template_id:
                query = query.filter(WorkerResourceDB.template_id == template_id)
                
            workers = query.order_by(WorkerResourceDB.name).all()
            self.logger.info(f"✅ Retrieved {len(workers)} workers for user {user_id}")
            return workers
            
        except Exception as e:
            self.logger.error(f"❌ Error getting user workers: {e}")
            return []
    
    def create_worker(self, worker_data: Dict[str, Any]) -> Optional[WorkerResourceDB]:
        """Create a new worker - NO COMMIT"""
        try:
            # Check if worker already exists for this user and code
            existing = self.db_session.query(WorkerResourceDB).filter(
                WorkerResourceDB.user_id == worker_data['user_id'],
                WorkerResourceDB.code == worker_data['code']
            ).first()
            
            if existing:
                self.logger.warning(f"⚠️ Worker already exists: {worker_data['code']}")
                return existing
            
            db_worker = WorkerResourceDB(**worker_data)
            self.db_session.add(db_worker)
            self.db_session.flush()
            self.logger.info(f"✅ Created new worker: {worker_data['name']}")
            return db_worker
            
        except Exception as e:
            self.logger.error(f"❌ Error creating worker: {e}")
            return None
    
    def update_worker(self, worker_id: int, user_id: int, updates: Dict[str, Any]) -> Optional[WorkerResourceDB]:
        """Update a worker by ID - NO COMMIT"""
        try:
            db_worker = self.db_session.query(WorkerResourceDB).filter(
                WorkerResourceDB.id == worker_id,
                WorkerResourceDB.user_id == user_id
            ).first()
            
            if db_worker:
                for key, value in updates.items():
                    if hasattr(db_worker, key) and key not in ['id', 'user_id', 'created_at']:
                        setattr(db_worker, key, value)
                self.db_session.flush()
                self.logger.info(f"✅ Updated worker ID: {worker_id}")
                return db_worker
            else:
                self.logger.warning(f"⚠️ Worker ID {worker_id} not found for user {user_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error updating worker: {e}")
            return None
    
    def delete_worker(self, worker_id: int, user_id: int) -> bool:
        """Soft delete a worker by ID - NO COMMIT"""
        try:
            db_worker = self.db_session.query(WorkerResourceDB).filter(
                WorkerResourceDB.id == worker_id,
                WorkerResourceDB.user_id == user_id
            ).first()
            
            if db_worker:
                db_worker.is_active = False
                self.db_session.flush()
                self.logger.info(f"✅ Soft deleted worker ID: {worker_id}")
                return True
            else:
                self.logger.warning(f"⚠️ Worker ID {worker_id} not found for user {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error deleting worker: {e}")
            return False
    
    # EQUIPMENT METHODS
    def get_user_equipment(self, user_id: int, template_id: Optional[int] = None) -> List[EquipmentResourceDB]:
        """Get all equipment for a user"""
        try:
            query = self.db_session.query(EquipmentResourceDB).filter(
                EquipmentResourceDB.user_id == user_id,
                EquipmentResourceDB.is_active == True
            )
            
            if template_id:
                query = query.filter(EquipmentResourceDB.template_id == template_id)
                
            equipment = query.order_by(EquipmentResourceDB.name).all()
            self.logger.info(f"✅ Retrieved {len(equipment)} equipment for user {user_id}")
            return equipment
            
        except Exception as e:
            self.logger.error(f"❌ Error getting user equipment: {e}")
            return []
    
    def create_equipment(self, equipment_data: Dict[str, Any]) -> Optional[EquipmentResourceDB]:
        """Create a new equipment - NO COMMIT"""
        try:
            # Check if equipment already exists for this user and code
            existing = self.db_session.query(EquipmentResourceDB).filter(
                EquipmentResourceDB.user_id == equipment_data['user_id'],
                EquipmentResourceDB.code == equipment_data['code']
            ).first()
            
            if existing:
                self.logger.warning(f"⚠️ Equipment already exists: {equipment_data['code']}")
                return existing
            
            db_equipment = EquipmentResourceDB(**equipment_data)
            self.db_session.add(db_equipment)
            self.db_session.flush()
            self.logger.info(f"✅ Created new equipment: {equipment_data['name']}")
            return db_equipment
            
        except Exception as e:
            self.logger.error(f"❌ Error creating equipment: {e}")
            return None
    
    def update_equipment(self, equipment_id: int, user_id: int, updates: Dict[str, Any]) -> Optional[EquipmentResourceDB]:
        """Update an equipment by ID - NO COMMIT"""
        try:
            db_equipment = self.db_session.query(EquipmentResourceDB).filter(
                EquipmentResourceDB.id == equipment_id,
                EquipmentResourceDB.user_id == user_id
            ).first()
            
            if db_equipment:
                for key, value in updates.items():
                    if hasattr(db_equipment, key) and key not in ['id', 'user_id', 'created_at']:
                        setattr(db_equipment, key, value)
                self.db_session.flush()
                self.logger.info(f"✅ Updated equipment ID: {equipment_id}")
                return db_equipment
            else:
                self.logger.warning(f"⚠️ Equipment ID {equipment_id} not found for user {user_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error updating equipment: {e}")
            return None
    
    def delete_equipment(self, equipment_id: int, user_id: int) -> bool:
        """Soft delete an equipment by ID - NO COMMIT"""
        try:
            db_equipment = self.db_session.query(EquipmentResourceDB).filter(
                EquipmentResourceDB.id == equipment_id,
                EquipmentResourceDB.user_id == user_id
            ).first()
            
            if db_equipment:
                db_equipment.is_active = False
                self.db_session.flush()
                self.logger.info(f"✅ Soft deleted equipment ID: {equipment_id}")
                return True
            else:
                self.logger.warning(f"⚠️ Equipment ID {equipment_id} not found for user {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error deleting equipment: {e}")
            return False
    
    # BULK OPERATIONS
    def get_template_with_resources(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get a template with all its resources"""
        try:
            template = self.db_session.query(ResourceTemplateDB).filter(
                ResourceTemplateDB.id == template_id
            ).first()
            
            if template:
                workers = self.get_workers_by_template(template_id)
                equipment = self.get_equipment_by_template(template_id)
                
                return {
                    'template': template,
                    'workers': workers,
                    'equipment': equipment
                }
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error getting template with resources: {e}")
            return None
    
    def count_template_resources(self, template_id: int) -> Dict[str, int]:
        """Count resources in a template"""
        try:
            worker_count = self.db_session.query(WorkerResourceDB).filter(
                WorkerResourceDB.template_id == template_id,
                WorkerResourceDB.is_active == True
            ).count()
            
            equipment_count = self.db_session.query(EquipmentResourceDB).filter(
                EquipmentResourceDB.template_id == template_id,
                EquipmentResourceDB.is_active == True
            ).count()
            
            return {
                'workers': worker_count,
                'equipment': equipment_count,
                'total': worker_count + equipment_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error counting template resources: {e}")
            return {'workers': 0, 'equipment': 0, 'total': 0}
        
    def get_worker_by_id(self, worker_id: int):
        """Get worker by ID"""
        try:
            return self.db_session.query(WorkerResourceDB).filter(
            WorkerResourceDB.id == worker_id
            ).first()
        except Exception as e:
            self.logger.error(f"Error getting worker by ID: {e}")
            return None

    def get_equipment_by_id(self, equipment_id: int):
        """Get equipment by ID"""
        try:
            return self.db_session.query(EquipmentResourceDB).filter(
            EquipmentResourceDB.id == equipment_id
            ).first()
        except Exception as e:
            self.logger.error(f"Error getting equipment by ID: {e}")
            return None

    def get_template_by_id(self, template_id: int):
        """Get template by ID"""
        try:
            return self.db_session.query(ResourceTemplateDB).filter(
            ResourceTemplateDB.id == template_id
            ).first()
        except Exception as e:
            self.logger.error(f"Error getting template by ID: {e}")
            return None