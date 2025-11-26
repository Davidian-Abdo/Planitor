"""
FIXED Schedule repository - No transaction control
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_

from backend.models.db_models import ScheduleDB, ScheduleTaskDB

logger = logging.getLogger(__name__)

class ScheduleRepository:
    """FIXED Schedule data repository - no commits"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_project_schedules(self, project_id: int, limit: int = 10) -> List[ScheduleDB]:
        """Get schedules for a project with task counts"""
        try:
            return self.session.query(ScheduleDB).options(
                joinedload(ScheduleDB.tasks)
            ).filter(
                ScheduleDB.project_id == project_id
            ).order_by(
                desc(ScheduleDB.generated_at)
            ).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Failed to get project schedules: {e}")
            return []
    
    def get_schedule_by_id(self, schedule_id: int) -> Optional[ScheduleDB]:
        """Get schedule by ID with tasks"""
        try:
            return self.session.query(ScheduleDB).options(
                joinedload(ScheduleDB.tasks)
            ).filter(ScheduleDB.id == schedule_id).first()
        except Exception as e:
            logger.error(f"Failed to get schedule {schedule_id}: {e}")
            return None
    
    def create_schedule(self, schedule_data: Dict[str, Any]) -> Optional[ScheduleDB]:
        """Create new schedule - NO COMMIT"""
        try:
            schedule = ScheduleDB(**schedule_data)
            self.session.add(schedule)
            self.session.flush()
            return schedule
        except Exception as e:
            logger.error(f"Failed to create schedule: {e}")
            return None
    
    def get_user_schedules(self, user_id: int, limit: int = 20) -> List[ScheduleDB]:
        """Get all schedules for a user"""
        try:
            return self.session.query(ScheduleDB).filter(
                ScheduleDB.user_id == user_id
            ).order_by(
                desc(ScheduleDB.generated_at)
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get user schedules: {e}")
            return []
    
    def create_schedule_with_tasks(self, schedule_data: Dict[str, Any], tasks_data: List[Dict[str, Any]]) -> Optional[ScheduleDB]:
        """Create schedule with associated tasks - NO COMMIT"""
        try:
            # Create schedule
            schedule = ScheduleDB(**schedule_data)
            self.session.add(schedule)
            self.session.flush()  # Flush to get schedule ID
            
            # Create tasks
            for task_data in tasks_data:
                task_data['schedule_id'] = schedule.id
                task = ScheduleTaskDB(**task_data)
                self.session.add(task)
            
            self.session.flush()
            return schedule
            
        except Exception as e:
            logger.error(f"Failed to create schedule with tasks: {e}")
            return None