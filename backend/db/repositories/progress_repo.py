"""
Progress tracking repository with ORM-based queries
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_
from datetime import datetime, date, timedelta

from backend.models.db_models import ProgressUpdateDB, ScheduleTaskDB, ScheduleDB, ProjectDB

logger = logging.getLogger(__name__)

class ProgressRepository:
    """Progress tracking repository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_progress_update(self, progress_data: Dict[str, Any]) -> Optional[ProgressUpdateDB]:
        """Create progress update record"""
        try:
            progress = ProgressUpdateDB(**progress_data)
            self.session.add(progress)
            #self.session.commit()
            self.session.flush()
            return progress
        except Exception as e:
            logger.error(f"Failed to create progress update: {e}")
            #self.session.rollback()
            return None
    
    def get_task_progress_history(self, task_id: int, limit: int = 10) -> List[ProgressUpdateDB]:
        """Get progress history for a task"""
        try:
            return self.session.query(ProgressUpdateDB).filter(
                ProgressUpdateDB.task_id == task_id
            ).order_by(
                desc(ProgressUpdateDB.update_date)
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get task progress history: {e}")
            return []
    
    def get_recent_activity(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent user activity using ORM"""
        try:
            # Get progress updates
            progress_updates = self.session.query(ProgressUpdateDB).options(
                joinedload(ProgressUpdateDB.task).joinedload(ScheduleTaskDB.schedule).joinedload(ScheduleDB.project)
            ).filter(
                ProgressUpdateDB.user_id == user_id
            ).order_by(
                desc(ProgressUpdateDB.update_date)
            ).limit(limit).all()
            
            activities = []
            for update in progress_updates:
                activities.append({
                    'activity_type': 'progress_update',
                    'activity_date': update.update_date,
                    'project_name': update.task.schedule.project.name if update.task and update.task.schedule and update.task.schedule.project else 'Unknown',
                    'task_name': update.task.name if update.task else 'Unknown',
                    'completion_percentage': update.completion_percentage,
                    'schedule_name': None
                })
            
            # Get schedule generations
            schedules = self.session.query(ScheduleDB).options(
                joinedload(ScheduleDB.project)
            ).filter(
                ScheduleDB.user_id == user_id
            ).order_by(
                desc(ScheduleDB.generated_at)
            ).limit(limit).all()
            
            for schedule in schedules:
                activities.append({
                    'activity_type': 'schedule_generated',
                    'activity_date': schedule.generated_at,
                    'project_name': schedule.project.name if schedule.project else 'Unknown',
                    'task_name': None,
                    'completion_percentage': None,
                    'schedule_name': schedule.name
                })
            
            # Sort by date and limit
            activities.sort(key=lambda x: x['activity_date'], reverse=True)
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return []
    
    def cleanup_old_data(self, older_than_days: int = 365) -> int:
        """Clean up old data using ORM (PostgreSQL compatible)"""
        try:
            cutoff_date = datetime.now().date() - timedelta(days=older_than_days)
            
            # Delete old progress updates
            progress_deleted = self.session.query(ProgressUpdateDB).filter(
                ProgressUpdateDB.update_date < cutoff_date
            ).delete()
            
            # Archive old completed schedules
            archive_updated = self.session.query(ScheduleDB).filter(
                and_(
                    ScheduleDB.generated_at < cutoff_date,
                    ScheduleDB.status == 'completed'
                )
            ).update({'status': 'archived'})
            
            #self.session.commit()
            self.session.flush()
            logger.info(f"Data cleanup completed: {progress_deleted} progress updates deleted, {archive_updated} schedules archived")
            return progress_deleted + archive_updated
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
            #self.session.rollback()
            return 0