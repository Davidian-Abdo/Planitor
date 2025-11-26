"""
Data table components for French Construction Project Planner
"""

from .schedule_table import render_schedule_table, render_task_details, render_critical_path_table
from .configuration_table import render_zones_table, render_work_sequences_table, render_project_config_table
from .performance_table import render_kpi_table, render_evm_table, render_risk_register
from .progress_table import render_progress_table, render_scurve_data

from frontend.components.data_tables.task_table import render_tasks_table
from frontend.components.data_tables.worker_table import render_workers_table
from frontend.components.data_tables.equipment_table import render_equipment_table


__all__ = [
    'render_schedule_table',
    'render_task_details',
    'render_critical_path_table',
    'render_resource_table', 
    'render_equipment_table',
    'render_utilization_table',
    'render_zones_table',
    'render_work_sequences_table',
    'render_project_config_table',
    'render_kpi_table',
    'render_evm_table',
    'render_risk_register',
    'render_progress_table',
    'render_scurve_data',
    'render_tasks_table',
    'render_workers_table', 
    'render_equipment_table'
]