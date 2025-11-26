"""
PROFESSIONAL Reporting Service with Dependency Injection
Enhanced for compatibility with new architecture
"""
import logging
import pandas as pd
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ReportingService:
    """
    Professional reporting service with dependency injection
    """
    
    def __init__(self, db_session: Session):
        # ✅ Professional: Inject db_session
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        
        # Initialize repositories with dependency injection
        self._initialize_repositories()
    
    def _initialize_repositories(self):
        """Professional repository initialization with fallback"""
        try:
            from backend.db.repositories.report_repo import ReportRepository
            from backend.db.repositories.project_repo import ProjectRepository
            
            self.report_repo = ReportRepository(self.db_session)
            self.project_repo = ProjectRepository(self.db_session)
            self.logger.info("✅ Reporting repositories initialized successfully")
        except ImportError:
            self.logger.warning("⚠️ Repositories not available, using fallback implementation")
            self.report_repo = FallbackReportRepository()
            self.project_repo = FallbackProjectRepository()
    
    def generate_schedule_report(self, schedule_result) -> Dict:
        """
        Generate schedule report with dependency injection
        
        Args:
            schedule_result: Schedule result data
            
        Returns:
            Dict: Report data
        """
        try:
            report = {
                'project_duration': schedule_result.project_duration,
                'total_cost': schedule_result.total_cost,
                'critical_path_length': len(schedule_result.critical_path),
                'total_tasks': len(schedule_result.tasks),
                'resource_utilization': schedule_result.resource_utilization,
                'generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating schedule report: {e}")
            return {}
    
    def generate_performance_report(self, monitoring_data: Dict) -> Dict:
        """
        Generate performance report with dependency injection
        
        Args:
            monitoring_data: Monitoring data
            
        Returns:
            Dict: Performance report
        """
        try:
            report = {
                'executive_summary': monitoring_data.get('executive_summary', {}),
                'performance_metrics': monitoring_data.get('performance_metrics', {}),
                'recommendations': monitoring_data.get('recommendations', []),
                'generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {}
    
    def get_user_performance_metrics(self, user_id: int) -> Dict[str, Any]:
        """Get user performance metrics using repository"""
        try:
            if hasattr(self.report_repo, 'get_user_performance_metrics'):
                return self.report_repo.get_user_performance_metrics(user_id)
            return {}
        except Exception as e:
            self.logger.error(f"Error getting user performance metrics: {e}")
            return {}
    
    def generate_project_report(self, project_id: int) -> Dict[str, Any]:
        """Generate comprehensive project report using repositories"""
        try:
            if not hasattr(self.project_repo, 'get_project_by_id'):
                return {}
            
            # Get project data
            project = self.project_repo.get_project_by_id(project_id)
            if not project:
                return {}
            
            # Get project progress
            progress_summary = {}
            if hasattr(self.project_repo, 'get_project_progress_summary'):
                progress_summary = self.project_repo.get_project_progress_summary(project_id)
            
            # Get user metrics
            user_metrics = self.get_user_performance_metrics(project.user_id)
            
            report = {
                'project_info': {
                    'name': project.name,
                    'status': project.status,
                    'start_date': project.start_date.isoformat() if project.start_date else None,
                    'description': project.description
                },
                'progress_summary': progress_summary,
                'user_metrics': user_metrics,
                'report_generated': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating project report: {e}")
            return {}

class FallbackReportRepository:
    """Professional fallback repository for reports"""
    
    def get_user_performance_metrics(self, user_id: int) -> Dict[str, Any]:
        return {}

class FallbackProjectRepository:
    """Professional fallback repository for projects"""
    
    def get_project_by_id(self, project_id: int):
        return None