"""
Reporting and analytics repository
"""
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from backend.models.db_models import ProjectDB, ScheduleDB, ScheduleTaskDB, ProgressUpdateDB

logger = logging.getLogger(__name__)

class ReportRepository:
    """Reporting and analytics repository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_user_performance_metrics(self, user_id: int) -> Dict[str, Any]:
        """Get user performance metrics"""
        try:
            # Project counts
            total_projects = self.session.query(ProjectDB).filter(
                ProjectDB.user_id == user_id
            ).count()
            
            active_projects = self.session.query(ProjectDB).filter(
                ProjectDB.user_id == user_id,
                ProjectDB.status.in_(['active', 'in_progress'])
            ).count()
            
            # Schedule metrics
            total_schedules = self.session.query(ScheduleDB).filter(
                ScheduleDB.user_id == user_id
            ).count()
            
            # Task completion metrics
            task_stats = self.session.query(
                func.avg(ScheduleTaskDB.completion_percentage).label('avg_completion'),
                func.count(ScheduleTaskDB.id).label('total_tasks')
            ).join(ScheduleDB).filter(
                ScheduleDB.user_id == user_id
            ).first()
            
            return {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'total_schedules': total_schedules,
                'avg_task_completion': float(task_stats.avg_completion or 0),
                'total_tasks': task_stats.total_tasks or 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get user performance metrics: {e}")
            return {}