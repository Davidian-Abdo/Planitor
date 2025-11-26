"""
SQLAlchemy database models for Construction Project Planner
Supports discipline-level zone sequencing and repository pattern
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, Text,
    ForeignKey, JSON, BigInteger
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.db.base import Base


# --- Users ---
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), nullable=False, default="user")
    company = Column(String(100))
    phone = Column(String(30))
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime)
    superviser = Column(String(60))
    password_changed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    projects = relationship("ProjectDB", back_populates="user", cascade="all, delete-orphan")
    task_templates = relationship("UserTaskTemplateDB", back_populates="user", cascade="all, delete-orphan")
    schedules = relationship("ScheduleDB", back_populates="user", cascade="all, delete-orphan")
    Resources_template = relationship("ResourceTemplateDB", back_populates="user", cascade="all, delete-orphan")
    Worker_template  = relationship("WorkerResourceDB", back_populates="user", cascade="all, delete-orphan")
    Equipment_template = relationship("EquipmentResourceDB", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("ReportDB", back_populates="user", cascade="all, delete-orphan")
    progress_updates = relationship("ProgressUpdateDB", back_populates="user", cascade="all, delete-orphan")


# --- Projects ---
class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    owner = Column(String(100))
    contract_number = Column(String(50))
    project_type = Column(String(50), default="Residential")
    status = Column(String(20), default="planned", index=True)
    start_date = Column(Date, index=True)
    target_end_date = Column(Date)
    actual_end_date = Column(Date)
    budget = Column(Float)
    actual_cost = Column(Float)
    currency = Column(String(3), default="EUR")
    floors = Column(Integer, default=1)  # kept for backward compatibility; actual floor counts are per-zone
    zones = Column(JSONB, default=dict)  # zones: list/dict of zone entries: [{'name': 'Zone A','max_floor': 5}, ...] - use JSONB
    constraints = Column(JSONB)
    assumptions = Column(JSONB)
    quantity_matrix_data = Column(JSONB)
    resource_data = Column(JSONB)
    equipment_data = Column(JSONB)
    zone_sequences = Column(JSON, nullable=False, default={})

    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserDB", back_populates="projects")
    schedules = relationship("ScheduleDB", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("ReportDB", back_populates="project", cascade="all, delete-orphan")
    # discipline sequences are stored in the DisciplineZoneSequenceDB table (see below)


# --- User Task Templates ---
class UserTaskTemplateDB(Base):
    __tablename__ = "user_task_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    base_task_id = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    discipline = Column(String(50), nullable=False, index=True)
    sub_discipline = Column(String(50), default="General")
    resource_type = Column(String(50), nullable=False)
    task_type = Column(String(20), default="worker")
    base_duration = Column(Integer, nullable=False)
    quantity = Column(Integer)
    unit = Column(String(20))
    unit_duration = Column(Integer )
    duration_calculation_method = Column(String, default="fixed_duration")
    min_crews_needed = Column(Integer, default=1)
    min_equipment_needed = Column(JSONB)
    predecessors = Column(JSONB)
    repeat_on_floor = Column(Boolean, default=True)
    delay = Column(Integer, default=0)
    weather_sensitive = Column(Boolean, default=False)
    quality_gate = Column(Boolean, default=False)
    included = Column(Boolean, default=True)
    max_crews_allowed = Column(Integer)
    max_equipment_allowed = Column(Integer)
    custom_fields = Column(JSONB)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    template_name = Column(String(20))
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserDB", back_populates="task_templates")

# --- Schedule & tasks ---
class ScheduleDB(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    version = Column(Integer, default=1)
    description = Column(Text)
    schedule_data = Column(JSONB, nullable=False)
    resource_allocations = Column(JSONB)
    project_duration = Column(Integer, nullable=False)
    total_cost = Column(Float, nullable=False)
    resource_utilization = Column(JSONB)
    critical_path = Column(JSONB)
    constraints_applied = Column(JSONB)
    assumptions_used = Column(JSONB)
    acceleration_factor = Column(Float, default=1.0)
    status = Column(String(20), default="generated")
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    baseline = Column(Boolean, default=False)
    parent_schedule_id = Column(Integer, ForeignKey("schedules.id"))

    project = relationship("ProjectDB", back_populates="schedules")
    user = relationship("UserDB", back_populates="schedules")
    progress_updates = relationship("ProgressUpdateDB", back_populates="schedule", cascade="all, delete-orphan")
    tasks = relationship("ScheduleTaskDB", back_populates="schedule", cascade="all, delete-orphan")
    parent_schedule = relationship("ScheduleDB", remote_side=[id], backref="child_schedules")


class ScheduleTaskDB(Base):
    __tablename__ = "schedule_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(150), nullable=False)
    base_task_id = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    discipline = Column(String(50), nullable=False, index=True)
    zone = Column(String(50), nullable=False)
    floor = Column(Integer, nullable=False)
    resource_type = Column(String(50), nullable=False)
    task_type = Column(String(20), nullable=False)
    base_duration = Column(Integer, nullable=False)
    min_crews_needed = Column(Integer, nullable=False)
    min_equipment_needed = Column(JSONB, nullable=False)
    predecessors = Column(JSONB, nullable=False)
    quantity = Column(Float, default=0.0)
    allocated_crews = Column(Integer, default=0)
    allocated_equipments = Column(JSONB)
    status = Column(String(20), default="planned", index=True)
    risk_factor = Column(Float, default=1.0)
    delay = Column(Integer, default=0)
    weather_sensitive = Column(Boolean, default=False)
    quality_gate = Column(Boolean, default=False)
    included = Column(Boolean, default=True)
    scheduled_start_date = Column(Date, index=True)
    scheduled_end_date = Column(Date, index=True)
    notes = Column(Text)

    schedule = relationship("ScheduleDB", back_populates="tasks")
    progress_updates = relationship("ProgressUpdateDB", back_populates="task")

class ProgressUpdateDB(Base):
    __tablename__ = "progress_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("schedule_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    update_date = Column(Date, nullable=False, index=True)
    completion_percentage = Column(Integer, nullable=False)
    hours_worked = Column(Float, default=0.0)
    resources_used = Column(JSONB)
    notes = Column(Text)
    issues_encountered = Column(Text)
    weather_impact = Column(String(50))
    delay_reason = Column(String(100))
    photos = Column(JSONB)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    schedule = relationship("ScheduleDB", back_populates="progress_updates")
    task = relationship("ScheduleTaskDB", back_populates="progress_updates")
    user = relationship("UserDB", back_populates="progress_updates")


class ReportDB(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"))
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="SET NULL"))
    report_type = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    report_data = Column(JSONB, nullable=False)
    parameters = Column(JSONB)
    format = Column(String(10), default="json")
    file_path = Column(String(500))
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)

    user = relationship("UserDB", back_populates="reports")
    project = relationship("ProjectDB", back_populates="reports")


class AuditLogDB(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer)
    details = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("UserDB")



# =============================================================================
# RESOURCE TEMPLATE TABLES - NEW
# =============================================================================

class ResourceTemplateDB(Base):
    __tablename__ = "resource_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), default="Default")
    version = Column(Integer, default=1)
    is_default = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserDB",back_populates="Resources_template")
    workers = relationship("WorkerResourceDB", back_populates="resource_template", cascade="all, delete-orphan")
    equipment = relationship("EquipmentResourceDB", back_populates="resource_template", cascade="all, delete-orphan")
    

class WorkerResourceDB(Base):
    __tablename__ = "worker_resources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("resource_templates.id", ondelete="CASCADE"), index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)
    specialty = Column(String(100), nullable=False)
    category = Column(String(50), default="Ouvrier")
    base_count = Column(Integer, default=1)
    hourly_rate = Column(Float, nullable=False)
    daily_rate = Column(Float)
    max_workers_per_crew = Column(Integer, default=1)
    base_productivity_rate = Column(Float, default=1.0)
    productivity_unit = Column(String(50), default="unités/jour")
    qualification_level = Column(String(50), default="Standard")
    skills = Column(JSONB)  # List of skills
    required_certifications = Column(JSONB)  # List of certifications
    is_active = Column(Boolean, default=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserDB",back_populates="Worker_template")
    resource_template = relationship("ResourceTemplateDB", back_populates="workers")
    template_id = Column(Integer, ForeignKey("resource_templates.id", ondelete="CASCADE"), index=True)

class EquipmentResourceDB(Base):
    __tablename__ = "equipment_resources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("resource_templates.id", ondelete="CASCADE"), index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)
    type = Column(String(100), nullable=False)
    category = Column(String(50), default="EnginLourd")
    model = Column(String(100))
    base_count = Column(Integer, default=1)
    hourly_rate = Column(Float, nullable=False)
    daily_rate = Column(Float)
    capacity = Column(String(100))
    max_units_per_task = Column(Integer, default=1)
    base_productivity_rate = Column(Float, default=1.0)
    productivity_unit = Column(String(50), default="unités/jour")
    requires_operator = Column(Boolean, default=True)
    operator_type = Column(String(100))
    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserDB",back_populates="Equipment_template")
    resource_template = relationship("ResourceTemplateDB", back_populates="equipment")
    template_id = Column(Integer, ForeignKey("resource_templates.id", ondelete="CASCADE"), index=True)