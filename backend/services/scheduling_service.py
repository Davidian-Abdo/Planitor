"""
FIXED Scheduling Service - Compatible with unified session management
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

# Domain models and helper components
from backend.models.domain_models import ScheduleResult
# Core components
from backend.core.calendar import AdvancedCalendar
from backend.core.duration import DurationCalculator
from backend.core.scheduler import AdvancedScheduler
from backend.core.task_generator import generate_tasks
# Repositories
from backend.db.repositories.schedule_repo import ScheduleRepository

logger = logging.getLogger(__name__)

class SchedulingService:
    """
    FIXED Scheduling Service - Pure scheduling logic
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.schedule_repo = ScheduleRepository(db_session)
        self.logger = logging.getLogger(__name__)

    def generate_schedule(
        self,
        user_id: int,
        quantity_file,
        resources_file,
        equipment_file,
        scheduling_params: Dict[str, Any],
    ) -> ScheduleResult:
        """
        Pure scheduling logic
        """
        try:
            self.logger.info(f"Starting optimized schedule generation for user {user_id}")

            # 1) Validate scheduling_params
            start_date = scheduling_params.get("start_date")
            if start_date is None:
                raise ValueError("scheduling_params must include 'start_date'")

            zones_floors = scheduling_params.get("zones_floors", {})
            project_id = scheduling_params.get("project_id")
            project_name = scheduling_params.get("project_name", "Generated Schedule")

            # 2) Parse input files -> structured dicts for scheduler
            parsed = self._parse_input_files(quantity_file, resources_file, equipment_file)

            # 3) Prepare domain WorkerResource and EquipmentResource objects
            workers_map = self._build_workers_map(parsed.get("workers", {}))
            equipment_map = self._build_equipment_map(parsed.get("equipment", {}))

            # 4) Build quantity structure
            quantity_matrix = parsed.get("quantity_matrix", {})

            # 5) Duration calculator + calendar
            duration_calc = DurationCalculator(workers_map, equipment_map, quantity_matrix)
            calendar = AdvancedCalendar(start_date)

            # 6) Get base tasks for scheduler
            base_tasks_dict = self._get_base_tasks_for_scheduler(user_id, project_id)

            # 7) Generate tasks for the project
            tasks = generate_tasks(
                base_tasks_dict=base_tasks_dict,
                zones_floors=zones_floors,
                cross_floor_links=scheduling_params.get("cross_floor_links", {}),
                ground_disciplines=scheduling_params.get("ground_disciplines", set()),
                discipline_zone_cfg=scheduling_params.get("discipline_zone_cfg", {}),
                user_id=user_id,
                project_id=project_id
            )

            # 8) Apply duration calculation methods
            tasks = self._apply_duration_calculation_methods(
                tasks, base_tasks_dict, quantity_matrix, duration_calc
            )

            # 9) Instantiate AdvancedScheduler and run
            scheduler = AdvancedScheduler(
                tasks=tasks,
                workers=workers_map,
                equipment=equipment_map,
                calendar=calendar,
                duration_calc=duration_calc
            )

            schedule_dict = scheduler.generate()
            self.logger.info(f"Scheduler returned {len(schedule_dict)} scheduled tasks")

            # 10) Create ScheduleResult domain object
            worker_allocations = getattr(scheduler.worker_manager, "allocations", {})
            equipment_allocations = getattr(scheduler.equipment_manager, "allocations", {})

            # Compute project metrics
            project_duration = self._compute_project_duration(schedule_dict, calendar)
            total_cost = self._calculate_total_cost(tasks, schedule_dict, workers_map, equipment_map)
            resource_utilization = self._compute_resource_utilization(scheduler, workers_map, equipment_map)
            critical_path = self._compute_critical_path(tasks, schedule_dict, calendar)

            schedule_result = ScheduleResult(
                tasks=tasks,
                schedule=schedule_dict,
                project_duration=project_duration,
                total_cost=total_cost,
                resource_utilization=resource_utilization,
                critical_path=critical_path,
                worker_manager=getattr(scheduler, "worker_manager", None),
                equipment_manager=getattr(scheduler, "equipment_manager", None),
                calendar=calendar,
                worker_allocations=worker_allocations,
                equipment_allocations=equipment_allocations
            )

            # 11) Persist schedule with enhanced task allocations
            try:
                schedule_record_id = self._persist_schedule_with_tasks(
                    project_id=project_id,
                    user_id=user_id,
                    name=project_name,
                    schedule_result=schedule_result,
                    params=scheduling_params
                )
                self.logger.info(f"Schedule persisted with tasks (id={schedule_record_id})")
            except Exception as e:
                self.logger.warning(f"Failed to persist schedule: {e}", exc_info=True)

            return schedule_result

        except Exception as exc:
            self.logger.error(f"Schedule generation failed: {exc}", exc_info=True)
            raise

    def _get_base_tasks_for_scheduler(self, user_id: int, project_id: Optional[int] = None):
        """Get base tasks for scheduler - optimized version"""
        try:
            from backend.services.user_task_service import UserTaskService
            task_service = UserTaskService(self.db_session)
            return task_service.get_user_base_tasks_for_scheduler(user_id, project_id)
        except Exception as e:
            self.logger.error(f"Error getting base tasks: {e}")
            from backend.defaults.TASKS import BASE_TASKS
            return BASE_TASKS

    def _apply_duration_calculation_methods(self, tasks, base_tasks_dict, quantity_matrix, duration_calc):
        """Apply duration calculation methods - optimized version"""
        updated_tasks = []
        
        for task in tasks:
            base_task = base_tasks_dict.get(task.base_id)
            if not base_task:
                self.logger.warning(f"Base task not found for {task.base_id}, using default duration")
                updated_tasks.append(task)
                continue
            
            duration_method = getattr(base_task, 'duration_calculation_method', 'fixed_duration')
            
            if duration_method == 'fixed_duration':
                task_duration = getattr(base_task, 'base_duration', 1)
                task.base_duration = task_duration
                
            elif duration_method == 'quantity_based':
                task_duration = self._calculate_quantity_based_duration(task, base_task, quantity_matrix)
                task.base_duration = task_duration
                
            elif duration_method == 'resource_calculation':
                task.base_duration = None
                
            else:
                task_duration = getattr(base_task, 'base_duration', 1)
                task.base_duration = task_duration
            
            updated_tasks.append(task)
        
        return updated_tasks

    def _calculate_quantity_based_duration(self, task, base_task, quantity_matrix):
        """Calculate quantity-based duration - optimized version"""
        try:
            unit_duration = getattr(base_task, 'unit_duration', 0.1)
            task_quantity = self._get_task_quantity(task, quantity_matrix)
            
            if task_quantity > 0:
                calculated_duration = task_quantity * unit_duration
                return max(0.5, calculated_duration)
            else:
                return unit_duration
                
        except Exception as e:
            self.logger.error(f"Error calculating quantity-based duration for {task.id}: {e}")
            return getattr(base_task, 'base_duration', getattr(base_task, 'unit_duration', 1))

    def _get_task_quantity(self, task, quantity_matrix):
        """Get task quantity - optimized version"""
        try:
            base_id_quantities = quantity_matrix.get(task.base_id, {})
            floor_quantities = base_id_quantities.get(task.floor, {})
            quantity = floor_quantities.get(task.zone, 0.0)
            return quantity
            
        except Exception as e:
            self.logger.warning(f"Could not get quantity for task {task.id}: {e}")
            return 0.0

    def _parse_input_files(self, quantity_file, resources_file, equipment_file):
        """Parse input files - optimized version"""
        import pandas as pd
        parsed = {}

        # Quantity matrix (required)
        try:
            df_q = pd.read_excel(quantity_file)
            parsed["quantity_matrix"] = self._parse_quantity_df(df_q)
        except Exception as e:
            self.logger.error(f"Failed to parse quantity file: {e}")
            raise

        # Workers (optional)
        if resources_file:
            try:
                df_workers = pd.read_excel(resources_file)
                parsed["workers"] = self._parse_workers_df(df_workers)
            except Exception as e:
                self.logger.warning(f"Could not parse resources file; using defaults. Error: {e}")
                parsed["workers"] = {}
        else:
            parsed["workers"] = {}

        # Equipment (optional)
        if equipment_file:
            try:
                df_equip = pd.read_excel(equipment_file)
                parsed["equipment"] = self._parse_equipment_df(df_equip)
            except Exception as e:
                self.logger.warning(f"Could not parse equipment file; using defaults. Error: {e}")
                parsed["equipment"] = {}
        else:
            parsed["equipment"] = {}

        return parsed

    def _parse_quantity_df(self, df):
        """Parse quantity DataFrame - optimized version"""
        required = {"TaskID", "Zone", "Floor", "Quantity"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Quantity template missing columns: {missing}")

        qm = {}
        for _, row in df.iterrows():
            task_id = str(row["TaskID"])
            zone = str(row["Zone"])
            floor = int(row["Floor"])
            qty = float(row["Quantity"])

            qm.setdefault(task_id, {}).setdefault(floor, {})[zone] = qty

        return qm

    def _parse_workers_df(self, df):
        """Parse workers DataFrame - optimized version"""
        import json
        result = {}
        for _, r in df.iterrows():
            name = str(r.get("ResourceName") or r.get("Name") or "").strip()
            if not name:
                continue

            result[name] = {
                "count": int(r.get("Count", 1)),
                "hourly_rate": float(r.get("HourlyRate", 0.0)),
                "productivity_rates": self._safe_json_parse(r.get("ProductivityRates", {})),
                "skills": self._parse_skills(r.get("Skills", "")),
                "max_crews": self._safe_json_parse(r.get("MaxCrews", {})),
                "efficiency": float(r.get("Efficiency", 1.0))
            }
        return result

    def _parse_equipment_df(self, df):
        """Parse equipment DataFrame - optimized version"""
        import json
        result = {}
        for _, r in df.iterrows():
            name = str(r.get("EquipmentName") or r.get("Name") or "").strip()
            if not name:
                continue

            result[name] = {
                "count": int(r.get("Count", 1)),
                "hourly_rate": float(r.get("HourlyRate", 0.0)),
                "productivity_rates": self._safe_json_parse(r.get("ProductivityRates", {})),
                "type": r.get("Type", "general"),
                "max_equipment": self._safe_json_parse(r.get("MaxEquipment", {})),
                "efficiency": float(r.get("Efficiency", 1.0))
            }
        return result

    def _safe_json_parse(self, value):
        """Safely parse JSON values"""
        import json
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return {}
        return value if value is not None else {}

    def _parse_skills(self, skills):
        """Parse skills string into list"""
        if isinstance(skills, str):
            return [s.strip() for s in skills.split(",") if s.strip()]
        return skills if skills else []

    def _build_workers_map(self, uploaded_workers):
        """Build workers map - optimized version"""
        from backend.models.domain_models import WorkerResource
        from backend.defaults.resources import workers as DEFAULT_WORKERS

        workers_map = {}

        # Defaults
        for name, default in DEFAULT_WORKERS.items():
            try:
                if isinstance(default, WorkerResource):
                    workers_map[name] = default
                else:
                    workers_map[name] = WorkerResource(
                        name=name,
                        count=getattr(default, "count", default.get("count", 1)),
                        hourly_rate=getattr(default, "hourly_rate", default.get("hourly_rate", 0.0)),
                        productivity_rates=getattr(default, "productivity_rates", default.get("productivity_rates", {})),
                        skills=getattr(default, "skills", default.get("skills", [])),
                        max_crews=getattr(default, "max_crews", default.get("max_crews", {})),
                        efficiency=getattr(default, "efficiency", default.get("efficiency", 1.0))
                    )
            except Exception:
                workers_map[name] = WorkerResource(name=name, count=1, hourly_rate=0.0)

        # Override with uploaded
        for name, spec in uploaded_workers.items():
            workers_map[name] = WorkerResource(
                name=name,
                count=int(spec.get("count", 1)),
                hourly_rate=float(spec.get("hourly_rate", 0.0)),
                productivity_rates=spec.get("productivity_rates", {}),
                skills=spec.get("skills", []),
                max_crews=spec.get("max_crews", {}),
                efficiency=float(spec.get("efficiency", 1.0))
            )

        return workers_map

    def _build_equipment_map(self, uploaded_equipment):
        """Build equipment map - optimized version"""
        from backend.models.domain_models import EquipmentResource
        from backend.defaults.resources import equipment as DEFAULT_EQUIPMENT

        equipment_map = {}

        # Defaults
        for name, default in DEFAULT_EQUIPMENT.items():
            try:
                if isinstance(default, EquipmentResource):
                    equipment_map[name] = default
                else:
                    equipment_map[name] = EquipmentResource(
                        name=name,
                        count=getattr(default, "count", default.get("count", 1)),
                        hourly_rate=getattr(default, "hourly_rate", default.get("hourly_rate", 0.0)),
                        productivity_rates=getattr(default, "productivity_rates", default.get("productivity_rates", {})),
                        type=getattr(default, "type", default.get("type", "general")),
                        max_equipment=getattr(default, "max_equipment", default.get("max_equipment", {})),
                        efficiency=getattr(default, "efficiency", default.get("efficiency", 1.0))
                    )
            except Exception:
                equipment_map[name] = EquipmentResource(name=name, count=1, hourly_rate=0.0)

        # Override with uploaded
        for name, spec in uploaded_equipment.items():
            equipment_map[name] = EquipmentResource(
                name=name,
                count=int(spec.get("count", 1)),
                hourly_rate=float(spec.get("hourly_rate", 0.0)),
                productivity_rates=spec.get("productivity_rates", {}),
                type=spec.get("type", "general"),
                max_equipment=spec.get("max_equipment", {}),
                efficiency=float(spec.get("efficiency", 1.0))
            )

        return equipment_map

    def _compute_project_duration(self, schedule, calendar):
        """Compute project duration - optimized version"""
        if not schedule:
            return 0
        
        start_dates = [s[0] for s in schedule.values() if s[0] is not None]
        end_dates = [s[1] for s in schedule.values() if s[1] is not None]
        
        if not start_dates or not end_dates:
            return 0
            
        project_start = min(start_dates)
        project_end = max(end_dates)
        
        # Count working days
        days = 0
        d = project_start
        while d <= project_end:
            if calendar.is_work_day(d):
                days += 1
            d = calendar.add_calendar_days(d, 1)
        return days

    def _calculate_total_cost(self, tasks, schedule, workers_map, equipment_map):
        """Calculate total cost with proper field access - UPDATED"""
        total = 0.0
        for task in tasks:
            if task.id not in schedule:
                continue
                
            start, end = schedule[task.id]
            duration_days = (end - start).days or 1
            
            # ✅ FIXED: Use consistent attribute names with getattr
            crews = getattr(task, "allocated_crews", None) or getattr(task, "min_crews_needed", 0)
            allocated_equipments = getattr(task, "allocated_equipments", {}) or {}
            
            # Labour cost
            if crews and task.resource_type in workers_map:
                worker = workers_map[task.resource_type]
                total += worker.hourly_rate * 8 * crews * duration_days
            
            # Equipment cost - FIXED: use allocated_equipments (plural)
            for equip_name, units in allocated_equipments.items():
                if equip_name in equipment_map:
                    equip = equipment_map[equip_name]
                    total += equip.hourly_rate * 8 * units * duration_days
                    
        return total

    def _compute_resource_utilization(self, scheduler, workers_map, equipment_map):
        """Compute resource utilization - optimized version"""
        utilization = {}
        wm = getattr(scheduler, "worker_manager", None)
        em = getattr(scheduler, "equipment_manager", None)

        if wm and hasattr(wm, "allocations"):
            for wname, allocs in wm.allocations.items():
                capacity = workers_map.get(wname).count if wname in workers_map else 0
                peak = max((alloc[2] if len(alloc) > 2 else 0) for alloc in allocs) if allocs else 0
                utilization[wname] = (peak / capacity) if capacity else 0.0

        if em and hasattr(em, "allocations"):
            for ename, allocs in em.allocations.items():
                capacity = equipment_map.get(ename).count if ename in equipment_map else 0
                peak = max((alloc[2] if len(alloc) > 2 else 0) for alloc in allocs) if allocs else 0
                utilization[ename] = (peak / capacity) if capacity else 0.0

        return utilization

    def _compute_critical_path(self, tasks, schedule, calendar):
        """Compute critical path - optimized version"""
        try:
            durations = {}
            for t in tasks:
                if t.id in schedule:
                    start, end = schedule[t.id]
                    # Count working days
                    dcount = 0
                    d = start
                    while d <= end:
                        if calendar.is_work_day(d):
                            dcount += 1
                        d = calendar.add_calendar_days(d, 1)
                    durations[t.id] = dcount
                    
            sorted_tasks = sorted(durations.items(), key=lambda x: x[1], reverse=True)
            return [tid for tid, _ in sorted_tasks[:max(1, min(10, len(sorted_tasks)))]]
        except Exception:
            return []

    def _persist_schedule_with_tasks(self, project_id, user_id, name, schedule_result, params):
        """Persist schedule with detailed task allocations - ENHANCED VERSION"""
        try:
            # Convert schedule to storage format
            schedule_data = {
                "schedule": {tid: [sd.isoformat(), ed.isoformat()] 
                            for tid, (sd, ed) in schedule_result.schedule.items()},
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "project_duration": schedule_result.project_duration,
                    "total_tasks": len(schedule_result.tasks),
                    "scheduling_params": params
                }
            }
            
            # Store task-level allocations
            task_allocations = {}
            schedule_tasks_data = []
            
            for task in schedule_result.tasks:
                if task.id in schedule_result.schedule:
                    start_date, end_date = schedule_result.schedule[task.id]
                    
                    # Task allocation record
                    task_allocations[task.id] = {
                        'crews': getattr(task, 'allocated_crews', 0),
                        'equipment': getattr(task, 'allocated_equipments', {}),
                        'duration': (end_date - start_date).days,
                        'cost': self._calculate_task_cost(task, schedule_result.schedule[task.id], 
                                                         schedule_result.worker_allocations, 
                                                         schedule_result.equipment_allocations)
                    }
                    
                    # ScheduleTasksDB record
                    schedule_task_data = {
                        'schedule_id': None,  # Will be set after schedule creation
                        'project_id': project_id,
                        'user_id': user_id,
                        'base_task_id': getattr(task, 'base_id', task.id),
                        'task_name': task.name,
                        'task_unique_id': task.id,
                        'discipline': getattr(task, 'discipline', 'Unknown'),
                        'sub_discipline': getattr(task, 'sub_discipline', ''),
                        'resource_type': getattr(task, 'resource_type', ''),
                        'task_type': getattr(task, 'task_type', 'execution'),
                        'zone': getattr(task, 'zone', ''),
                        'floor': getattr(task, 'floor', 0),
                        'scheduled_start_date': start_date,
                        'scheduled_end_date': end_date,
                        'planned_duration': (end_date - start_date).days,
                        'allocated_crews': getattr(task, 'allocated_crews', 0),  # ✅ ACTUAL allocation
                        'allocated_equipments': getattr(task, 'allocated_equipments', {}),  # ✅ ACTUAL allocation
                        'min_crews_needed': getattr(task, 'min_crews_needed', 1),
                        'max_crews_allowed': getattr(task, 'max_crews_allowed', 1),
                        'min_equipment_needed': getattr(task, 'min_equipment_needed', {}),
                        'max_equipment_allowed': getattr(task, 'max_equipment_allowed', {}),
                        'status': 'scheduled',
                        'is_critical_path': task.id in getattr(schedule_result, 'critical_path', []),
                        'predecessors': getattr(task, 'predecessors', [])
                    }
                    schedule_tasks_data.append(schedule_task_data)
            
            # Create schedule record
            schedule_record_data = {
                "project_id": project_id,
                "user_id": user_id,
                "name": name,
                "version": 1,
                "description": f"Schedule generated for {name}",
                "schedule_data": schedule_data,
                "resource_allocations": {
                    "workers": schedule_result.worker_allocations,
                    "equipment": schedule_result.equipment_allocations
                },
                "task_allocations": task_allocations,  # ✅ NEW: Store task-level allocations
                "project_duration": schedule_result.project_duration,
                "total_cost": schedule_result.total_cost,
                "resource_utilization": schedule_result.resource_utilization,
                "critical_path": schedule_result.critical_path,
                "status": "generated",
                "baseline": True,
                "generated_at": datetime.utcnow()
            }
            
            # Create schedule and associated tasks using enhanced repository method
            created_schedule = self.schedule_repo.create_schedule_with_tasks(
                schedule_record_data, schedule_tasks_data
            )
            
            if created_schedule:
                self.logger.info(f"✅ Schedule persisted with {len(schedule_tasks_data)} task records")
                return created_schedule.id
            else:
                self.logger.error("❌ Failed to persist schedule with tasks")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error persisting schedule with tasks: {e}")
            return None

    def _calculate_task_cost(self, task, schedule_dates, worker_allocations, equipment_allocations):
        """Calculate individual task cost"""
        try:
            start_date, end_date = schedule_dates
            duration_days = (end_date - start_date).days or 1
            total_cost = 0.0
            
            # Labor cost
            allocated_crews = getattr(task, 'allocated_crews', 0)
            if allocated_crews > 0 and hasattr(task, 'resource_type'):
                # This would need access to worker rates - simplified for now
                total_cost += allocated_crews * duration_days * 500  # Placeholder rate
            
            # Equipment cost
            allocated_equipments = getattr(task, 'allocated_equipments', {})
            for equip_name, units in allocated_equipments.items():
                total_cost += units * duration_days * 200  # Placeholder rate
                
            return total_cost
            
        except Exception as e:
            self.logger.warning(f"Could not calculate task cost for {task.id}: {e}")
            return 0.0

    def save_schedule(self, user_id: int, schedule_data: Dict) -> bool:
        """Save schedule to database - compatibility method"""
        try:
            created = self.schedule_repo.create_schedule(schedule_data)
            return created is not None
        except Exception as e:
            self.logger.error(f"Error saving schedule: {e}")
            return False
    