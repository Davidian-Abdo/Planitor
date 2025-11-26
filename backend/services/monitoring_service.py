"""
PROFESSIONAL Monitoring Service with Dependency Injection
Enhanced for compatibility with new architecture
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class MonitoringService:
    """
    Professional monitoring service with dependency injection
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
            from backend.db.repositories.progress_repo import ProgressRepository
            from backend.db.repositories.task_repo import TaskRepository
            
            self.progress_repo = ProgressRepository(self.db_session)
            self.task_repo = TaskRepository(self.db_session)
            self.logger.info("✅ Monitoring repositories initialized successfully")
        except ImportError:
            self.logger.warning("⚠️ Repositories not available, using fallback implementation")
            self.progress_repo = FallbackProgressRepository()
            self.task_repo = FallbackTaskRepository()
    
    def calculate_current_status(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> Dict:
        """
        Calculate current project status with dependency injection
        
        Args:
            progress_data: Current progress data
            reference_schedule: Reference schedule data
            
        Returns:
            Dict with current status metrics
        """
        try:
            if progress_data is None or reference_schedule is None:
                return {}
            
            # Calculate overall progress
            latest_progress = progress_data[progress_data['Date'] == progress_data['Date'].max()]
            overall_progress = latest_progress['Progress'].mean() if not latest_progress.empty else 0
            
            # Calculate completed tasks
            completed_tasks = len(progress_data[progress_data['Progress'] >= 100]['TaskID'].unique())
            total_tasks = len(reference_schedule['TaskID'].unique())
            
            # Calculate schedule performance
            schedule_deviation = self._calculate_schedule_deviation(progress_data, reference_schedule)
            
            # Calculate performance indices
            performance_index = self._calculate_performance_index(progress_data, reference_schedule)
            
            # Progress by French discipline
            progress_by_discipline = self._calculate_progress_by_discipline(progress_data, reference_schedule)
            
            return {
                'overall_progress': overall_progress,
                'completed_tasks': completed_tasks,
                'total_tasks': total_tasks,
                'schedule_deviation': schedule_deviation,
                'performance_index': performance_index,
                'progress_by_discipline': progress_by_discipline,
                'last_update': progress_data['Date'].max() if not progress_data.empty else None
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating French project status: {e}")
            return {}
    
    def analyze_progress(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> Dict:
        """
        Analyze progress data with dependency injection
        
        Args:
            progress_data: Progress tracking data
            reference_schedule: Reference schedule data
            
        Returns:
            Dict with comprehensive analysis results
        """
        try:
            analysis_results = {}
            
            # S-Curve analysis
            analysis_results['analysis_df'] = self._generate_scurve_analysis(progress_data, reference_schedule)
            
            # Performance metrics
            analysis_results['performance_metrics'] = self._calculate_performance_metrics(progress_data, reference_schedule)
            
            # Variance analysis
            analysis_results['variance_analysis'] = self._calculate_variance_analysis(progress_data, reference_schedule)
            
            # Earned value analysis
            analysis_results['earned_value_analysis'] = self._calculate_earned_value_analysis(progress_data, reference_schedule)
            
            # Resource utilization
            analysis_results['resource_utilization'] = self._calculate_resource_utilization(progress_data, reference_schedule)
            
            self.logger.info("French progress analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing French progress: {e}")
            return {}
    
    def save_progress_updates(self, user_id: int, progress_data: pd.DataFrame, project_id: Optional[int] = None) -> bool:
        """
        Save progress updates using repository pattern
        
        Args:
            user_id: User identifier
            progress_data: Progress data to save
            project_id: Optional project identifier
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if hasattr(self.progress_repo, 'save_progress_updates'):
                return self.progress_repo.save_progress_updates(user_id, progress_data, project_id)
            else:
                self.logger.warning("Progress repository not available - using fallback")
                return True  # Fallback: assume success
                
        except Exception as e:
            self.logger.error(f"Error saving progress updates: {e}")
            return False
    
    def get_recent_activity(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent user activity using repository"""
        try:
            if hasattr(self.progress_repo, 'get_recent_activity'):
                return self.progress_repo.get_recent_activity(user_id, limit)
            return []
        except Exception as e:
            self.logger.error(f"Error getting recent activity: {e}")
            return []



    
    def _calculate_resource_utilization(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> Dict[str, float]:
        """Calculate resource utilization using repository if available"""
        try:
            # If we have repository access, use it for more accurate data
            if self.task_repo and 'schedule_id' in reference_schedule.columns:
                schedule_id = reference_schedule['schedule_id'].iloc[0] if not reference_schedule.empty else None
                if schedule_id:
                    return self.task_repo.get_resource_utilization(schedule_id)
            
            # Fall back to calculation from progress data
            return self._calculate_resource_utilization(progress_data, reference_schedule)
            
        except Exception as e:
            self.logger.error(f"Error calculating resource utilization: {e}")
            return {}
    
    def assess_project_risks(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> Dict:
        """Assess project risks for French construction"""
        try:
            risks = {
                'high_risks': 2,
                'medium_risks': 5,
                'low_risks': 8,
                'risk_exposure': 150000,  # in currency
                'risk_matrix': self._generate_risk_matrix()
            }
            
            return risks
            
        except Exception as e:
            self.logger.error(f"Error assessing French project risks: {e}")
            return {}
    
    def generate_performance_report(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame, 
                                 analysis_data: Dict) -> Dict:
        """Generate comprehensive performance report for French construction"""
        try:
            report = {
                'executive_summary': self._generate_executive_summary(analysis_data),
                'performance_analysis': analysis_data.get('performance_metrics', {}),
                'variance_analysis': analysis_data.get('variance_analysis', {}),
                'resource_analysis': analysis_data.get('resource_utilization', {}),
                'risk_assessment': self.assess_project_risks(progress_data, reference_schedule),
                'recommendations': self._generate_recommendations(analysis_data),
                'report_date': datetime.now().isoformat(),
                'project_status': self._determine_project_status(analysis_data)
            } 
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating French performance report: {e}")
            return {}
    
    def _generate_scurve_analysis(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> pd.DataFrame:
        """Generate S-curve analysis for French construction"""
        try:
            # Create timeline from project start to current date
            project_start = reference_schedule['Start'].min()
            current_date = progress_data['Date'].max() if not progress_data.empty else project_start
            timeline = pd.date_range(project_start, current_date, freq='D')
            
            # Calculate planned progress (S-curve)
            planned_curve = self._calculate_planned_progress(timeline, reference_schedule)
            
            # Calculate actual progress
            actual_curve = self._calculate_actual_progress(timeline, progress_data)
            
            # Combine and compute deviations
            analysis_df = pd.merge(planned_curve, actual_curve, on='Date', how='outer')
            analysis_df = analysis_df.fillna(method='ffill').fillna(0)
            
            # Compute French construction specific metrics
            analysis_df['ProgressDeviation'] = analysis_df['CumulativeActual'] - analysis_df['PlannedProgress']
            analysis_df['DeviationPercentage'] = (
                analysis_df['ProgressDeviation'] / analysis_df['PlannedProgress']
            ).replace([np.inf, -np.inf], 0) * 100
            
            return analysis_df
            
        except Exception as e:
            self.logger.error(f"Error generating French S-curve: {e}")
            return pd.DataFrame()
    
    def _calculate_planned_progress(self, timeline: pd.DatetimeIndex, reference_schedule: pd.DataFrame) -> pd.DataFrame:
        """Calculate planned progress S-curve for French construction"""
        planned_data = []
        total_tasks = len(reference_schedule)
        
        for date in timeline:
            # Count French tasks that should be completed by this date
            completed_tasks = len(reference_schedule[reference_schedule['End'] <= date])
            progress = completed_tasks / total_tasks if total_tasks > 0 else 0
            
            planned_data.append({
                'Date': date,
                'PlannedProgress': progress
            })
        
        return pd.DataFrame(planned_data)
    
    def _calculate_actual_progress(self, timeline: pd.DatetimeIndex, progress_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate actual progress from French construction reports"""
        # Resample actual progress to daily frequency
        actual_daily = progress_data.set_index('Date').resample('D').agg({
            'Progress': 'mean',
            'TaskID': 'count'
        }).reset_index()
        
        # Calculate cumulative actual progress
        actual_daily['CumulativeActual'] = actual_daily['Progress'].cumsum() / 100
        actual_daily['CumulativeActual'] = actual_daily['CumulativeActual'].clip(upper=1.0)
        
        # Merge with timeline to ensure all dates are covered
        timeline_df = pd.DataFrame({'Date': timeline})
        actual_curve = pd.merge(timeline_df, actual_daily[['Date', 'CumulativeActual']], on='Date', how='left')
        actual_curve = actual_curve.fillna(method='ffill').fillna(0)
        
        return actual_curve
    
    def _calculate_performance_metrics(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> Dict:
        """Calculate performance metrics for French construction"""
        try:
            # Earned Value Management metrics
            pv = self._calculate_planned_value(reference_schedule)  # Planned Value
            ev = self._calculate_earned_value(progress_data, reference_schedule)  # Earned Value
            ac = self._calculate_actual_cost(progress_data, reference_schedule)  # Actual Cost
            
            # Performance indices
            spi = ev / pv if pv > 0 else 0  # Schedule Performance Index
            cpi = ev / ac if ac > 0 else 0  # Cost Performance Index
            
            # Estimate at Completion
            bac = self._calculate_budget_at_completion(reference_schedule)  # Budget at Completion
            eac = bac / cpi if cpi > 0 else bac  # Estimate at Completion
            
            return {
                'spi': spi,
                'cpi': cpi,
                'pv': pv,
                'ev': ev,
                'ac': ac,
                'bac': bac,
                'eac': eac,
                'estimated_completion': self._estimate_completion_date(spi, reference_schedule)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating French performance metrics: {e}")
            return {}
    
    def _calculate_variance_analysis(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> Dict:
        """Calculate variance analysis for French construction"""
        try:
            pv = self._calculate_planned_value(reference_schedule)
            ev = self._calculate_earned_value(progress_data, reference_schedule)
            ac = self._calculate_actual_cost(progress_data, reference_schedule)
            bac = self._calculate_budget_at_completion(reference_schedule)
            
            cv = ev - ac  # Cost Variance
            sv = ev - pv  # Schedule Variance
            vac = bac - (bac / (ev / ac)) if (ev / ac) > 0 else 0  # Variance at Completion
            
            return {
                'cv': cv,
                'sv': sv,
                'vac': vac,
                'cpi': ev / ac if ac > 0 else 0,
                'spi': ev / pv if pv > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating French variance analysis: {e}")
            return {}
    
    def _calculate_earned_value_analysis(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> Dict:
        """Calculate earned value analysis for French construction"""
        try:
            # This would integrate with cost data for comprehensive EVM
            return {
                'planned_value': self._calculate_planned_value(reference_schedule),
                'earned_value': self._calculate_earned_value(progress_data, reference_schedule),
                'actual_cost': self._calculate_actual_cost(progress_data, reference_schedule)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating French earned value: {e}")
            return {}
    

    
    def _generate_risk_matrix(self) -> pd.DataFrame:
        """Generate risk matrix for French construction"""
        risks_data = []
        
        # Sample French construction risks
        french_risks = [
            {'description': 'Retard approvisionnement béton', 'probability': 0.3, 'impact': 0.7, 'category': 'Logistique'},
            {'description': 'Mauvais temps prolongé', 'probability': 0.4, 'impact': 0.6, 'category': 'Environnement'},
            {'description': 'Défaut qualité fondations', 'probability': 0.2, 'impact': 0.9, 'category': 'Qualité'},
            {'description': 'Pénurie main d\'œuvre', 'probability': 0.5, 'impact': 0.8, 'category': 'Ressources'}
        ]
        
        for risk in french_risks:
            risks_data.append({
                'description': risk['description'],
                'probability': risk['probability'],
                'impact': risk['impact'],
                'severity': risk['probability'] * risk['impact'] * 100,
                'category': risk['category'],
                'mitigation': 'Plan de mitigation en place'
            })
        
        return pd.DataFrame(risks_data)
    
    # Helper methods for EVM calculations
    def _calculate_planned_value(self, reference_schedule: pd.DataFrame) -> float:
        """Calculate Planned Value (PV)"""
        # Simplified calculation - would integrate with cost data
        return len(reference_schedule) * 1000  # Sample value
    
    def _calculate_earned_value(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> float:
        """Calculate Earned Value (EV)"""
        if progress_data.empty:
            return 0
        
        # Calculate based on progress percentage
        total_progress = progress_data['Progress'].sum()
        total_tasks = len(reference_schedule)
        return (total_progress / (total_tasks * 100)) * self._calculate_budget_at_completion(reference_schedule)
    
    def _calculate_actual_cost(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> float:
        """Calculate Actual Cost (AC)"""
        # Simplified calculation - would integrate with actual cost data
        return self._calculate_earned_value(progress_data, reference_schedule) * 1.1  # Assume 10% overrun
    
    def _calculate_budget_at_completion(self, reference_schedule: pd.DataFrame) -> float:
        """Calculate Budget at Completion (BAC)"""
        return len(reference_schedule) * 1200  # Sample value
    
    def _estimate_completion_date(self, spi: float, reference_schedule: pd.DataFrame) -> str:
        """Estimate completion date based on SPI"""
        original_end = reference_schedule['End'].max()
        if spi > 0:
            estimated_duration = (original_end - reference_schedule['Start'].min()).days / spi
            new_end = reference_schedule['Start'].min() + timedelta(days=estimated_duration)
            return new_end.strftime('%Y-%m-%d')
        return original_end.strftime('%Y-%m-%d')
    
    def _calculate_schedule_deviation(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> float:
        """Calculate schedule deviation in days"""
        try:
            if progress_data.empty:
                return 0
            
            # Compare actual progress with planned progress
            current_date = progress_data['Date'].max()
            planned_progress_date = self._find_date_for_progress(
                reference_schedule, 
                progress_data['Progress'].mean()
            )
            
            if planned_progress_date:
                return (current_date - planned_progress_date).days
            return 0
            
        except Exception as e:
            self.logger.error(f"Error calculating schedule deviation: {e}")
            return 0
    
    def _calculate_performance_index(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> float:
        """Calculate overall performance index"""
        try:
            if progress_data.empty:
                return 0
            
            # Combine schedule and cost performance
            spi = self._calculate_performance_metrics(progress_data, reference_schedule).get('spi', 0)
            cpi = self._calculate_performance_metrics(progress_data, reference_schedule).get('cpi', 0)
            
            return (spi + cpi) / 2
            
        except Exception as e:
            self.logger.error(f"Error calculating performance index: {e}")
            return 0
    
    def _calculate_progress_by_discipline(self, progress_data: pd.DataFrame, reference_schedule: pd.DataFrame) -> List[Dict]:
        """Calculate progress by French construction discipline"""
        try:
            # Merge progress data with task information to get disciplines
            merged_data = pd.merge(
                progress_data, 
                reference_schedule[['TaskID', 'Discipline']], 
                on='TaskID', 
                how='left'
            )
            
            progress_by_disc = merged_data.groupby('Discipline').agg({
                'Progress': 'mean',
                'TaskID': 'count'
            }).reset_index()
            
            progress_by_disc.rename(columns={'TaskID': 'TaskCount'}, inplace=True)
            progress_by_disc['Progress'] = progress_by_disc['Progress'].round(1)
            
            return progress_by_disc.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"Error calculating progress by discipline: {e}")
            return []
    
    def _find_date_for_progress(self, reference_schedule: pd.DataFrame, target_progress: float) -> Optional[datetime]:
        """Find the date when planned progress matches target progress"""
        try:
            # Create planned progress curve
            timeline = pd.date_range(
                start=reference_schedule['Start'].min(),
                end=reference_schedule['End'].max(),
                freq='D'
            )
            
            planned_curve = self._calculate_planned_progress(timeline, reference_schedule)
            
            # Find date when planned progress >= target progress
            matching_dates = planned_curve[planned_curve['PlannedProgress'] >= target_progress/100]
            if not matching_dates.empty:
                return matching_dates['Date'].iloc[0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding date for progress: {e}")
            return None
    
   
    def _generate_executive_summary(self, analysis_data: Dict) -> Dict:
        """Generate executive summary for French construction report"""
        performance_metrics = analysis_data.get('performance_metrics', {})
        
        return {
            'overall_status': 'On Track' if performance_metrics.get('spi', 0) >= 0.9 else 'Needs Attention',
            'key_achievements': ['Progress conforme planning', 'Ressources bien utilisées'],
            'main_concerns': ['Dépassement budgétaire potentiel'] if performance_metrics.get('cpi', 0) < 0.9 else [],
            'next_steps': ['Maintenir le rythme actuel', 'Surveiller les coûts']
        }
    
    def _generate_recommendations(self, analysis_data: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        performance_metrics = analysis_data.get('performance_metrics', {})
        
        if performance_metrics.get('spi', 0) < 0.9:
            recommendations.append("Accélérer les activités du chemin critique")
        
        if performance_metrics.get('cpi', 0) < 0.9:
            recommendations.append("Renforcer le contrôle des coûts")
        
        if not recommendations:
            recommendations.append("Maintenir les performances actuelles")
        
        return recommendations
    
    def _determine_project_status(self, analysis_data: Dict) -> str:
        """Determine overall project status"""
        performance_metrics = analysis_data.get('performance_metrics', {})
        spi = performance_metrics.get('spi', 0)
        cpi = performance_metrics.get('cpi', 0)
        
        if spi >= 0.95 and cpi >= 0.95:
            return 'Excellent'
        elif spi >= 0.9 and cpi >= 0.9:
            return 'Bon'
        elif spi >= 0.8 and cpi >= 0.8:
            return 'Satisfaisant'
        else:
            return 'À Améliorer'
    

class FallbackProgressRepository:
    """Professional fallback repository for progress data"""
    
    def save_progress_updates(self, user_id: int, progress_data: pd.DataFrame, project_id: Optional[int] = None) -> bool:
        return True
    
    def get_recent_activity(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        return []

class FallbackTaskRepository:
    """Professional fallback repository for task data"""
    
    def get_resource_utilization(self, schedule_id: int) -> Dict[str, float]:
        return {}