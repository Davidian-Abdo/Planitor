"""
Professional scheduling reporter with Excel export capabilities
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import tempfile
import logging

from ..models.domain_models import (Task, ScheduleResult)

logger = logging.getLogger(__name__)


class SchedulingReporter:
    """
    Professional reporting engine for construction schedules
    Generates comprehensive Excel reports with multiple sheets
    """
    
    def __init__(self, tasks: List[Task], schedule: Dict[str, Tuple[datetime, datetime]],
                 worker_manager, equipment_manager, calendar):
        self.tasks = tasks
        self.schedule = schedule
        self.worker_manager = worker_manager
        self.equipment_manager = equipment_manager
        self.calendar = calendar
        self.logger = logging.getLogger(__name__)

    def export_schedule_excel(self, file_path: str) -> str:
        """
        Export main schedule to Excel with professional formatting
        """
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Main schedule sheet
                self._export_main_schedule(writer)
                
                # Resource allocation sheet
                self._export_resource_allocation(writer)
                
                # Task details sheet
                self._export_task_details(writer)
                
                # Summary sheet
                self._export_project_summary(writer)
                
            self.logger.info(f"✅ Schedule exported to: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export schedule: {e}")
            raise

    def _export_main_schedule(self, writer: pd.ExcelWriter) -> None:
        """Export main schedule sheet"""
        rows = []
        for task in self.tasks:
            if task.id in self.schedule:
                start_date, end_date = self.schedule[task.id]
                duration = (end_date - start_date).days
                
                rows.append({
                    "Task ID": task.id,
                    "Task Name": task.name,
                    "Discipline": task.discipline,
                    "Sub-Discipline": getattr(task, 'sub_discipline', 'General'),
                    "Zone": task.zone,
                    "Floor": task.floor,
                    "Start Date": start_date.strftime('%Y-%m-%d'),
                    "End Date": end_date.strftime('%Y-%m-%d'),
                    "Duration (Days)": duration,
                    "Resource Type": task.resource_type,
                    "Task Type": task.task_type.value,
                    "Crews Allocated": task.allocated_crews or "",
                    "Equipment Allocated": self._format_equipment(task.allocated_equipment),
                    "Quantity": task.quantity,
                    "Status": task.status.value
                })
        
        df = pd.DataFrame(rows)
        df.to_excel(writer, sheet_name="Main Schedule", index=False)
        
        # Auto-adjust columns
        worksheet = writer.sheets["Main Schedule"]
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    def _export_resource_allocation(self, writer: pd.ExcelWriter) -> None:
        """Export resource allocation details"""
        # Worker allocations
        worker_rows = []
        for res_name, allocations in self.worker_manager.allocations.items():
            for (task_id, _, units_used, start, end) in allocations:
                worker_rows.append({
                    "Resource Type": "Worker",
                    "Resource Name": res_name,
                    "Task ID": task_id,
                    "Units Used": units_used,
                    "Start Date": start.strftime('%Y-%m-%d'),
                    "End Date": end.strftime('%Y-%m-%d'),
                    "Duration (Days)": (end - start).days
                })
        
        # Equipment allocations
        equipment_rows = []
        for res_name, allocations in self.equipment_manager.allocations.items():
            for (task_id, _, units_used, start, end) in allocations:
                equipment_rows.append({
                    "Resource Type": "Equipment",
                    "Resource Name": res_name,
                    "Task ID": task_id,
                    "Units Used": units_used,
                    "Start Date": start.strftime('%Y-%m-%d'),
                    "End Date": end.strftime('%Y-%m-%d'),
                    "Duration (Days)": (end - start).days
                })
        
        # Combine and export
        all_allocations = worker_rows + equipment_rows
        if all_allocations:
            df = pd.DataFrame(all_allocations)
            df.to_excel(writer, sheet_name="Resource Allocation", index=False)

    def _export_task_details(self, writer: pd.ExcelWriter) -> None:
        """Export detailed task information"""
        rows = []
        for task in self.tasks:
            rows.append({
                "Task ID": task.id,
                "Base Task ID": task.base_id,
                "Task Name": task.name,
                "Discipline": task.discipline,
                "Zone": task.zone,
                "Floor": task.floor,
                "Resource Type": task.resource_type,
                "Task Type": task.task_type.value,
                "Min Crews Needed": task.min_crews_needed or "",
                "Min Equipment Needed": self._format_equipment(task.min_equipment_needed),
                "Base Duration": task.base_duration,
                "Quantity": task.quantity,
                "Risk Factor": task.risk_factor,
                "Predecessors": ", ".join(task.predecessors) if task.predecessors else "",
                "Delay (Days)": task.delay,
                "Weather Sensitive": task.weather_sensitive,
                "Included": task.included
            })
        
        df = pd.DataFrame(rows)
        df.to_excel(writer, sheet_name="Task Details", index=False)

    def _export_project_summary(self, writer: pd.ExcelWriter) -> None:
        """Export project summary statistics"""
        scheduled_tasks = [t for t in self.tasks if t.id in self.schedule]
        
        if scheduled_tasks:
            start_dates = [self.schedule[t.id][0] for t in scheduled_tasks]
            end_dates = [self.schedule[t.id][1] for t in scheduled_tasks]
            
            project_start = min(start_dates)
            project_end = max(end_dates)
            project_duration = (project_end - project_start).days
            
            summary_data = {
                "Metric": [
                    "Total Tasks", "Scheduled Tasks", "Project Start Date", 
                    "Project End Date", "Project Duration (Days)", "Total Zones",
                    "Total Floors", "Tasks with Delays", "Weather Sensitive Tasks"
                ],
                "Value": [
                    len(self.tasks),
                    len(scheduled_tasks),
                    project_start.strftime('%Y-%m-%d'),
                    project_end.strftime('%Y-%m-%d'),
                    project_duration,
                    len(set(t.zone for t in self.tasks)),
                    len(set(t.floor for t in self.tasks)),
                    len([t for t in self.tasks if t.delay > 0]),
                    len([t for t in self.tasks if t.weather_sensitive])
                ]
            }
            
            df = pd.DataFrame(summary_data)
            df.to_excel(writer, sheet_name="Project Summary", index=False)

    def _format_equipment(self, equipment_dict: Optional[Dict[str, int]]) -> str:
        """Format equipment dictionary for display"""
        if not equipment_dict:
            return ""
        return ", ".join([f"{k}:{v}" for k, v in equipment_dict.items()])

    def export_resource_utilization(self, output_dir: str, freq: str = 'D') -> Dict[str, str]:
        """
        Export time-phased resource utilization reports
        Returns paths to generated files
        """
        os.makedirs(output_dir, exist_ok=True)
        output_files = {}
        
        try:
            # Worker utilization
            worker_file = os.path.join(output_dir, "worker_utilization.xlsx")
            self._export_time_phased_utilization(
                self.worker_manager.allocations, worker_file, "Worker", freq
            )
            output_files['workers'] = worker_file
            
            # Equipment utilization
            equipment_file = os.path.join(output_dir, "equipment_utilization.xlsx")
            self._export_time_phased_utilization(
                self.equipment_manager.allocations, equipment_file, "Equipment", freq
            )
            output_files['equipment'] = equipment_file
            
            self.logger.info("✅ Resource utilization reports generated")
            return output_files
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export resource utilization: {e}")
            raise

    def _export_time_phased_utilization(self, allocations, file_path: str, 
                                      resource_type: str, freq: str) -> None:
        """Export time-phased resource utilization"""
        rows = []
        
        for res_name, resource_allocations in allocations.items():
            for (task_id, _, units_used, start, end) in resource_allocations:
                current_date = start
                while current_date < end:
                    rows.append({
                        "Date": current_date.strftime('%Y-%m-%d'),
                        "Resource Type": resource_type,
                        "Resource Name": res_name,
                        "Task ID": task_id,
                        "Units Used": units_used
                    })
                    current_date += timedelta(days=1)
        
        if rows:
            df = pd.DataFrame(rows)
            
            if freq == 'W':
                # Weekly aggregation
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.groupby([
                    pd.Grouper(key='Date', freq='W-MON'), 
                    'Resource Type', 'Resource Name', 'Task ID'
                ])['Units Used'].sum().reset_index()
            
            df.to_excel(file_path, index=False)

    def export_all_reports(self, base_folder: str = None) -> str:
        """
        Export all reports to a folder
        Returns path to the reports folder
        """
        if base_folder is None:
            base_folder = tempfile.mkdtemp(prefix="schedule_reports_")
        
        os.makedirs(base_folder, exist_ok=True)
        
        try:
            # Main schedule
            schedule_file = os.path.join(base_folder, "construction_schedule.xlsx")
            self.export_schedule_excel(schedule_file)
            
            # Resource utilization
            util_folder = os.path.join(base_folder, "resource_utilization")
            self.export_resource_utilization(util_folder)
            
            # CPM Analysis
            cpm_file = os.path.join(base_folder, "critical_path_analysis.xlsx")
            self.export_cpm_analysis(cpm_file)
            
            self.logger.info(f"✅ All reports exported to: {base_folder}")
            return base_folder
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export all reports: {e}")
            raise

    def export_cpm_analysis(self, file_path: str) -> str:
        """
        Export Critical Path Method analysis
        """
        try:
            from ..core.CPM import CPMAnalyzer
            
            durations = {
                t.id: max(1, (self.schedule[t.id][1] - self.schedule[t.id][0]).days)
                for t in self.tasks if t.id in self.schedule
            }
            dependencies = {t.id: t.predecessors for t in self.tasks}
            
            cpm = CPMAnalyzer(list(durations.keys()), durations, dependencies)
            cpm.analyze()
            
            rows = []
            for task in self.tasks:
                if task.id in cpm.ES:
                    es_date = self.calendar.add_workdays(self.calendar.current_date, cpm.ES[task.id])
                    ef_date = self.calendar.add_workdays(self.calendar.current_date, cpm.EF[task.id])
                    ls_date = self.calendar.add_workdays(self.calendar.current_date, cpm.LS[task.id])
                    lf_date = self.calendar.add_workdays(self.calendar.current_date, cpm.LF[task.id])
                    
                    rows.append({
                        "Task ID": task.id,
                        "Task Name": task.name,
                        "Discipline": task.discipline,
                        "Duration (Days)": durations[task.id],
                        "Early Start": es_date.strftime('%Y-%m-%d'),
                        "Early Finish": ef_date.strftime('%Y-%m-%d'),
                        "Late Start": ls_date.strftime('%Y-%m-%d'),
                        "Late Finish": lf_date.strftime('%Y-%m-%d'),
                        "Total Float": cpm.float[task.id],
                        "Critical Path": "Yes" if cpm.float[task.id] == 0 else "No"
                    })
            
            df = pd.DataFrame(rows)
            df.to_excel(file_path, sheet_name="CPM Analysis", index=False)
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export CPM analysis: {e}")
            raise
