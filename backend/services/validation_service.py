"""
PROFESSIONAL Validation Service with Dependency Injection
Enhanced for compatibility with new architecture
"""
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Professional validation service with dependency injection
    """
    
    def __init__(self, db_session: Session):
        # ✅ Professional: Inject db_session for potential future repository use
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
    
    def validate_french_tasks(self, tasks: List, workers: Dict, equipment: Dict, quantity_matrix: Dict) -> List:
        """
        Validate tasks against French construction standards with dependency injection
        
        Args:
            tasks: List of tasks to validate
            workers: Available workers
            equipment: Available equipment
            quantity_matrix: Quantity data
            
        Returns:
            List: Validated tasks
        """
        validated_tasks = []
        
        for task in tasks:
            # Validate resource availability
            if task.resource_type in workers:
                worker = workers[task.resource_type]
                if task.min_crews_needed > worker.count:
                    self.logger.warning(f"Task {task.id} requires {task.min_crews_needed} crews but only {worker.count} available")
            
            # Validate equipment availability
            for equip_name, units_needed in task.min_equipment_needed.items():
                if equip_name in equipment:
                    equip = equipment[equip_name]
                    if units_needed > equip.count:
                        self.logger.warning(f"Task {task.id} requires {units_needed} {equip_name} but only {equip.count} available")
            
            # Validate quantity data exists
            if hasattr(task, 'base_id') and task.base_id in quantity_matrix:
                if task.floor in quantity_matrix[task.base_id]:
                    if task.zone in quantity_matrix[task.base_id][task.floor]:
                        task.quantity = quantity_matrix[task.base_id][task.floor][task.zone]
            
            validated_tasks.append(task)
        
        return validated_tasks
    
    def validate_project_parameters(self, params: Dict) -> Dict:
        """
        Validate project parameters with dependency injection
        
        Args:
            params: Project parameters
            
        Returns:
            Dict: Validation results
        """
        issues = []
        
        # Check required parameters
        required_params = ['start_date', 'zones_floors']
        for param in required_params:
            if param not in params:
                issues.append(f"Missing required parameter: {param}")
        
        # Validate start date
        if 'start_date' in params:
            try:
                from datetime import datetime
                datetime.strptime(str(params['start_date']), '%Y-%m-%d')
            except ValueError:
                issues.append("Invalid start date format. Use YYYY-MM-DD")
        
        # Validate zones and floors
        if 'zones_floors' in params:
            zones_floors = params['zones_floors']
            if not isinstance(zones_floors, dict):
                issues.append("zones_floors must be a dictionary")
            else:
                for zone, floors in zones_floors.items():
                    if not isinstance(floors, list):
                        issues.append(f"Floors for zone {zone} must be a list")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }