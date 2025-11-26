from __future__ import annotations
import pandas as pd
from typing import Dict, List, Any
from .domain_models import Task, Project, ScheduleResult, ProjectProgress


def task_to_dict(task: Task) -> Dict[str, Any]:
    return {
        "id": task.id,
        "base_id": task.base_id,
        "name": task.name,
        "discipline": task.discipline,
        "subDiscipline": task.sub_discipline,
        "zone": task.zone,
        "floor": task.floor,
        "resourceType": task.resource_type,
        "taskType": task.task_type.value,
        "baseDuration": task.base_duration,
        "minCrews": task.min_crews_needed,
        "minEquipment": task.min_equipment_needed,
        "predecessors": task.predecessors,
        "quantity": task.quantity,
        "allocatedCrews": task.allocated_crews,
        "status": task.status.value,
        "risk": task.risk_factor,
        "delay": task.delay,
        "weatherSensitive": task.weather_sensitive,
        "qualityGate": task.quality_gate,
        "included": task.included,
    }


def project_to_dict(project: Project) -> Dict[str, Any]:
    return {
        "name": project.name,
        "description": project.description,
        "startDate": str(project.start_date),
        "zones": [{"name": z.name, "maxFloors": z.max_floors} for z in project.zones],
        "workSequences": [
            {
                "zone": seq.zone,
                "discipline": seq.discipline,
                "taskName": seq.task_name,
                "predecessors": seq.predecessor_tasks,
                "parallel": seq.parallel_tasks,
                "duration": seq.duration_days,
            }
            for seq in project.work_sequences
        ],
        "createdBy": project.created_by,
    }


def schedule_to_dataframe(schedule_result: ScheduleResult) -> pd.DataFrame:
    rows = []
    for task in schedule_result.tasks:
        if task.id in schedule_result.schedule:
            start_date, end_date = schedule_result.schedule[task.id]
            rows.append(
                {
                    "TaskID": task.id,
                    "TaskName": task.name,
                    "Discipline": task.discipline,
                    "SubDiscipline": task.sub_discipline,
                    "Zone": task.zone,
                    "Floor": task.floor,
                    "Start": start_date,
                    "End": end_date,
                    "Duration": (end_date - start_date).days,
                    "ResourceType": task.resource_type,
                    "AllocatedCrews": task.allocated_crews,
                    "Status": task.status.value,
                    "IsCritical": task.id in schedule_result.critical_path,
                }
            )
    return pd.DataFrame(rows)


def progress_to_dataframe(progress_records: List[ProjectProgress]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "TaskID": p.task_id,
                "Date": p.date,
                "Progress": p.progress,
                "ActualStart": p.actual_start,
                "ActualEnd": p.actual_end,
                "Notes": p.notes,
            }
            for p in progress_records
        ]
    )


def task_template_to_domain(db_task) -> Dict[str, Any]:
    return {
        "id": db_task.task_id,
        "name": db_task.name,
        "discipline": db_task.discipline,
        "sub_discipline": db_task.sub_discipline,
        "resource_type": db_task.resource_type,
        "task_type": getattr(db_task.task_type, "value", db_task.task_type),
        "base_duration": db_task.base_duration,
        "min_crews_needed": db_task.min_crews_needed,
        "min_equipment_needed": db_task.min_equipment_needed or {},
        "predecessors": db_task.predecessors or [],
        "repeat_on_floor": db_task.repeat_on_floor,
        "delay": db_task.delay,
        "weather_sensitive": db_task.weather_sensitive,
        "quality_gate": db_task.quality_gate,
        "included": db_task.included,
    }


def project_db_to_domain(db_project):
    from .domain_models import Project, Zone
    zones = [
        Zone(
            name=z.name,
            max_floors=z.max_floors,
            sequence_order=z.sequence_order,
            description=z.description or "",
        )
        for z in db_project.zones
    ]
    return Project(
        name=db_project.name,
        description=db_project.description or "",
        start_date=db_project.start_date.date(),
        zones=zones,
        work_sequences=[],  # TODO: DB mapping needed here!
        created_by=db_project.created_by,
    )


def progress_db_to_domain(db_progress):
    return ProjectProgress(
        task_id=db_progress.task_id,
        date=db_progress.date.date(),
        progress=db_progress.progress,
        actual_start=db_progress.actual_start.date()
        if db_progress.actual_start
        else None,
        actual_end=db_progress.actual_end.date() if db_progress.actual_end else None,
        notes=db_progress.notes or "",
    )

def resource_to_dict(resource: Any) -> Dict[str, Any]:
    """Convert resource object to dictionary"""
    if hasattr(resource, 'name'):
        return {
            'name': resource.name,
            'count': resource.count,
            'hourly_rate': resource.hourly_rate,
            'productivity_rates': getattr(resource, 'productivity_rates', {}),
            'skills': getattr(resource, 'skills', []),
            'type': getattr(resource, 'type', 'worker'),
            'max_units': getattr(resource, 'max_crews', getattr(resource, 'max_equipment', 0)),
            'efficiency': getattr(resource, 'efficiency', 1.0)
        }
    return {}
def work_sequence_to_db(seq: dict, project_id: int):
    from .db_models import WorkSequenceDB
    return WorkSequenceDB(
        project_id=project_id,
        zone=seq['zone'],
        discipline=seq['discipline'],
        task_id=seq['task_id'],
        task_name=seq['task_name'],
        predecessors=seq.get('predecessors', []),
        parallel_tasks=seq.get('parallel_tasks', []),
        duration_days=seq.get('duration_days', 1)
    )
def work_sequence_db_to_domain(db_seq) :
    from .domain_models import WorkSequence
    return WorkSequence(
        zone=db_seq.zone,
        discipline=db_seq.discipline,
        task_name=db_seq.task_name,
        predecessor_tasks=db_seq.predecessors or [],
        parallel_tasks=db_seq.parallel_tasks or [],
        duration_days=db_seq.duration_days,
    )