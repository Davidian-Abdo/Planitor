

"""
Domain models supporting discipline-level zone sequencing
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional,Tuple, Any
from enum import Enum

class TaskType(Enum):
    WORKER = "worker"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    HYBRID = "hybrid"
    SUPERVISION = "supervision"

class TaskStatus(Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    ON_HOLD = "on_hold"

@dataclass
class BaseTask:
    id: str
    name: str
    discipline: str
    sub_discipline: str
    base_duration: int
    resource_type: str = "worker"
    task_type: TaskType = TaskType.WORKER
    min_crews_needed: int = 1
    min_equipment_needed: Dict[str, int] = field(default_factory=dict)
    predecessors: List[str] = field(default_factory=list)
    repeat_on_floor: bool = True
    delay: int = 0
    weather_sensitive: bool = False
    quality_gate: bool = False
    included: bool = True

@dataclass
class Task:
    id: str
    base_id: str
    name: str
    discipline: str
    sub_discipline: str
    zone: str
    floor: int
    base_duration: int
    resource_type: str
    task_type: TaskType
    min_crews_needed: int
    min_equipment_needed: Dict[str, int]
    predecessors: List[str]
    quantity: float = 0.0
    allocated_crews: int = 0
    allocated_equipment: Dict[str, int] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PLANNED
    risk_factor: float = 1.0
    delay: int = 0
    weather_sensitive: bool = False
    quality_gate: bool = False
    included: bool = True

@dataclass
class Zone:
    name: str
    max_floors: int
    sequence_order: int = 0
    description: str = ""

@dataclass
class DisciplineZoneSequence:
    discipline: str
    groups: List[List[str]] = field(default_factory=list)
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None

@dataclass
class Project:
    name: str
    description: str
    start_date: date
    zone_floors: List[Zone]
    zone_sequences: Dict[str, List] 
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ScheduleResult:
    """Scheduling results for French construction"""
    tasks: List[Task]
    schedule: Dict[str, Tuple[datetime, datetime]]
    project_duration: int
    total_cost: float
    resource_utilization: Dict[str, float]
    critical_path: List[str]
    worker_manager: Any = None
    equipment_manager: Any = None
    calendar: Any = None

@dataclass
class ProjectProgress:
    """Progress tracking for French construction"""
    task_id: str
    date: date
    progress: float  # 0-100
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    notes: str = ""

@dataclass
class PerformanceMetrics:
    """Performance metrics for French construction"""
    schedule_performance: float  # SPI
    cost_performance: float  # CPI
    quality_score: float
    safety_index: float
    productivity_index: float
    overall_performance: float

@dataclass
class WorkerResource:
    """French construction worker resource"""
    name: str
    count: int
    hourly_rate: float
    productivity_rates: Dict[str, float] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
    max_crews: Dict[str, int] = field(default_factory=dict)
    efficiency: float = 1.0

    @property
    def cost_per_day(self) -> float:
        """Calculate daily cost for French worker"""
        return self.hourly_rate * 8  # 8-hour work day

@dataclass
class EquipmentResource:
    """French construction equipment resource"""
    name: str
    count: int
    hourly_rate: float
    productivity_rates: Dict[str, float] = field(default_factory=dict)
    type: str = "general"
    max_equipment: int = 0
    efficiency: float = 1.0

    @property
    def cost_per_day(self) -> float:
        """Calculate daily cost for French equipment"""
        return self.hourly_rate * 8  # 8-hour work day