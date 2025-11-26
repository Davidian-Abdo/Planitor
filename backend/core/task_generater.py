"""
Enhanced task generator with user customizations, better error handling, and optimized performance
"""
import logging
from typing import Dict, List, Set, Optional, Any

from ..models.domain_models import (Task, BaseTask, TaskType, TaskStatus)

logger = logging.getLogger(__name__)


def generate_tasks(
    base_tasks_dict: Dict[str, BaseTask],
    zone_floors: Dict[str, int],
    cross_floor_links: Dict[str, List[str]] = None,
    ground_disciplines: Set[str] = None,
    discipline_zone_cfg: Dict[str, Any] = None,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None
) -> List[Task]:
    """Generate tasks with optional discipline-level zone sequencing"""
    try:
        cross_floor_links = cross_floor_links or {}
        ground_disciplines = ground_disciplines or set()
        discipline_zone_cfg = discipline_zone_cfg or {}

        _validate_generation_inputs(base_tasks_dict, zone_floors)
        task_id_registry = _build_task_id_registry(base_tasks_dict, zone_floors, ground_disciplines)

        tasks = _generate_tasks_with_dependencies(
            base_tasks_dict=base_tasks_dict,
            zone_floors=zone_floors,
            task_id_registry=task_id_registry,
            cross_floor_links=cross_floor_links,
            ground_disciplines=ground_disciplines,
            discipline_zone_cfg=discipline_zone_cfg
        )

        _validate_generated_tasks(tasks, task_id_registry)
        logger.info(f"✅ Successfully generated {len(tasks)} tasks")
        return tasks

    except Exception as e:
        logger.error(f"❌ Task generation failed: {e}")
        raise TaskGenerationError(str(e)) from e


def _generate_tasks_with_dependencies(
    base_tasks_dict: Dict[str, BaseTask],
    zone_floors: Dict[str, int],
    task_id_registry: Set[str],
    cross_floor_links: Dict[str, List[str]],
    ground_disciplines: Set[str],
    discipline_zone_cfg: Dict[str, Any]
) -> List[Task]:
    """Generate tasks and resolve all dependencies"""
    tasks = []
    base_by_id = {task.id: task for task in base_tasks_dict.values() if getattr(task, "included", True)}

    for base_id, base_task in base_by_id.items():
        # User-defined discipline-level sequencing
        discipline_sequence = discipline_zone_cfg.get(base_task.discipline)
        if discipline_sequence:
            # Build sequential groups and parallel mapping
            zone_groups = [[z['zone']] for z in discipline_sequence]
            parallel_mapping = {z['zone']: z.get('parallel_with', []) for z in discipline_sequence}
            strategy_type = "group_sequential"
        else:
            # Default: all zones fully parallel
            zone_groups = [list(zone_floors.keys())]
            parallel_mapping = {}
            strategy_type = "fully_parallel"

        for group_idx, zone_group in enumerate(zone_groups):
            for zone in zone_group:
                max_floor = zone_floors[zone]
                floor_range = _get_floor_range(base_task, max_floor, ground_disciplines)

                for floor in floor_range:
                    task_id = f"{base_id}-F{floor}-{zone}"
                    predecessors = _resolve_all_dependencies(
                        base_task=base_task,
                        task_id=task_id,
                        zone=zone,
                        floor=floor,
                        task_id_registry=task_id_registry,
                        base_by_id=base_by_id,
                        cross_floor_links=cross_floor_links,
                        zone_group=zone_group,
                        group_idx=group_idx,
                        strategy_type=strategy_type,
                        zone_groups=zone_groups,
                        parallel_mapping=parallel_mapping
                    )

                    task = _create_task(base_task, task_id, predecessors, zone, floor)
                    tasks.append(task)
    return tasks


def _resolve_all_dependencies(
    base_task: BaseTask,
    task_id: str,
    zone: str,
    floor: int,
    task_id_registry: Set[str],
    base_by_id: Dict[str, BaseTask],
    cross_floor_links: Dict[str, List[str]],
    zone_group: List[str],
    group_idx: int,
    strategy_type: str,
    zone_groups: List[List[str]],
    parallel_mapping: Dict[str, List[str]] = None
) -> List[str]:
    """Resolve dependencies including user-defined cross-zone sequences"""
    predecessors = set()

    # Regular and cross-floor dependencies
    predecessors.update(_resolve_regular_predecessors(base_task, zone, floor, task_id_registry, base_by_id))
    predecessors.update(_resolve_cross_floor_links(base_task, zone, floor, task_id_registry, base_by_id, cross_floor_links))
    predecessors.update(_resolve_same_task_vertical_dependencies(base_task, task_id, zone, floor, task_id_registry))
    predecessors.update(_resolve_user_custom_dependencies(base_task, zone, floor, task_id_registry))

    # Cross-zone dependencies
    if strategy_type == "group_sequential" and group_idx > 0:
        prev_group = zone_groups[group_idx - 1]
        for prev_zone in prev_group:
            cross_zone_task = f"{base_task.id}-F{floor}-{prev_zone}"
            if cross_zone_task in task_id_registry:
                # Skip if current zone is parallel with previous zone
                if parallel_mapping and prev_zone in parallel_mapping.get(zone, []):
                    continue
                predecessors.add(cross_zone_task)

    # Remove self-reference
    predecessors.discard(task_id)
    return list(predecessors)


def _get_floor_range(base_task: BaseTask, max_floor: int, ground_disciplines: Set[str]) -> List[int]:
    """Calculate floor range for a base task"""
    if getattr(base_task, "ground_only", False) or base_task.discipline in ground_disciplines:
        return [0]

    custom_range = getattr(base_task, "custom_floor_range", None)
    if custom_range:
        return [f for f in custom_range if 0 <= f <= max_floor]

    start_floor = getattr(base_task, "start_floor", 0)
    end_floor = getattr(base_task, "end_floor", max_floor)
    return list(range(start_floor, min(end_floor, max_floor) + 1))


def _create_task(base_task: BaseTask, task_id: str, predecessors: List[str], zone: str, floor: int) -> Task:
    """Create a Task object with all attributes"""
    base_id = base_task.id
    return Task(
        id=task_id,
        base_id=base_id,
        name=base_task.name,
        discipline=base_task.discipline,
        zone=zone,
        floor=floor,
        resource_type=base_task.resource_type,
        task_type=base_task.task_type,
        base_duration=base_task.base_duration,
        min_crews_needed=base_task.min_crews_needed,
        min_equipment_needed=getattr(base_task, "min_equipment_needed", {}),
        predecessors=predecessors,
        quantity=0.0,
        allocated_crews=0,
        allocated_equipment={},
        status=TaskStatus.PLANNED,
        risk_factor=getattr(base_task, "risk_factor", 1.0),
        delay=getattr(base_task, "delay", 0),
        weather_sensitive=getattr(base_task, "weather_sensitive", False),
        quality_gate=getattr(base_task, "quality_gate", False),
        included=getattr(base_task, "included", True)
    )


def _validate_generation_inputs(base_tasks_dict: Dict[str, BaseTask], zone_floors: Dict[str, int]):
    if not base_tasks_dict:
        raise ValueError("Base tasks dictionary cannot be empty")
    if not zone_floors:
        raise ValueError("Zone floors configuration cannot be empty")


def _validate_generated_tasks(tasks: List[Task], task_id_registry: Set[str]):
    task_ids = set()
    for task in tasks:
        if task.id in task_ids:
            raise ValueError(f"Duplicate task ID: {task.id}")
        task_ids.add(task.id)

        for pred_id in task.predecessors:
            if pred_id not in task_id_registry and pred_id not in task_ids:
                logger.warning(f"⚠️ Missing predecessor reference: {pred_id} for task {task.id}")


def _validate_generation_inputs(base_tasks_dict: Dict[str, BaseTask], zone_floors: Dict[str, int]):
    """Validate input parameters for task generation"""
    if not base_tasks_dict:
        raise ValueError("Base tasks dictionary cannot be empty")
    
    if not zone_floors:
        raise ValueError("Zone floors configuration cannot be empty")
    
    for zone, max_floor in zone_floors.items():
        if max_floor < 0:
            raise ValueError(f"Invalid max_floor {max_floor} for zone {zone}")
        
    # Check for duplicate base task IDs
    base_task_ids = set()
    for task_id, task in base_tasks_dict.items():
        if task_id in base_task_ids:
            raise ValueError(f"Duplicate base task ID: {task_id}")
        base_task_ids.add(task_id)


def _build_task_id_registry(
    base_tasks_dict: Dict[str, BaseTask], 
    zone_floors: Dict[str, int], 
    ground_disciplines: Set[str]
) -> Set[str]:
    """
    Build optimized registry of all possible task IDs for quick lookup
    
    Returns:
        Set of all possible task IDs in format: "{base_id}-F{floor}-{zone}"
    """
    task_ids = set()
    
    for base_id, base_task in base_tasks_dict.items():
        if not getattr(base_task, "included", True):
            continue
            
        for zone, max_floor in zone_floors.items():
            floor_range = _get_floor_range(base_task, max_floor, ground_disciplines)
            
            for floor in floor_range:
                task_id = f"{base_id}-F{floor}-{zone}"
                task_ids.add(task_id)
    
    logger.debug(f"📋 Built task ID registry with {len(task_ids)} possible task combinations")
    return task_ids

def _resolve_all_dependencies(
    base_task: BaseTask,
    task_id: str,
    zone: str,
    floor: int,
    task_id_registry: Set[str],
    base_by_id: Dict[str, BaseTask],
    cross_floor_links: Dict[str, List[str]],
    zone_group: List[str],
    group_idx: int,
    strategy_type: str,
    zone_groups: List[List[str]]
) -> List[str]:
    """
    Resolve all types of dependencies for a task
    """
    predecessors = set()
    
    # 1. REGULAR PREDECESSORS (same floor, same zone)
    predecessors.update(_resolve_regular_predecessors(base_task, zone, floor, task_id_registry, base_by_id))
    
    # 2. PREDEFINED CROSS-FLOOR LINKS
    predecessors.update(_resolve_cross_floor_links(base_task, zone, floor, task_id_registry, base_by_id, cross_floor_links))
    
    # 3. CROSS-FLOOR SAME-TASK DEPENDENCY (vertical workflow)
    predecessors.update(_resolve_same_task_vertical_dependencies(base_task, task_id, zone, floor, task_id_registry))
    
    # 4. CROSS-ZONE DEPENDENCIES (zone sequencing)
    predecessors.update(_resolve_cross_zone_dependencies(
        base_task, task_id, zone, floor, group_idx, strategy_type, zone_groups, task_id_registry
    ))
    
    # 5. USER-CONFIGURED CUSTOM DEPENDENCIES
    predecessors.update(_resolve_user_custom_dependencies(base_task, zone, floor, task_id_registry))
    
    # Remove duplicates and self-references
    predecessors = [p for p in predecessors if p != task_id]
    
    return list(predecessors)


def _resolve_regular_predecessors(
    base_task: BaseTask,
    zone: str,
    floor: int,
    task_id_registry: Set[str],
    base_by_id: Dict[str, BaseTask]
) -> Set[str]:
    """Resolve regular predecessors (same floor, same zone)"""
    predecessors = set()
    
    for pred_base_id in base_task.predecessors:
        pred_base = base_by_id.get(pred_base_id)
        if pred_base:
            pred_floor = _get_predecessor_floor_optimized(pred_base, floor)
            pred_id = f"{pred_base_id}-F{pred_floor}-{zone}"
            if pred_id in task_id_registry:
                predecessors.add(pred_id)
    
    return predecessors


def _resolve_cross_floor_links(
    base_task: BaseTask,
    zone: str,
    floor: int,
    task_id_registry: Set[str],
    base_by_id: Dict[str, BaseTask],
    cross_floor_links: Dict[str, List[str]]
) -> Set[str]:
    """Resolve predefined cross-floor dependencies"""
    predecessors = set()
    
    if base_task.id in cross_floor_links:
        for pred_base_id in cross_floor_links[base_task.id]:
            pred_base = base_by_id.get(pred_base_id)
            if pred_base:
                # Default: depend on floor below, but allow configuration
                pred_floor = floor - 1
                if pred_floor >= 0:  # Ensure valid floor
                    pred_id = f"{pred_base_id}-F{pred_floor}-{zone}"
                    if pred_id in task_id_registry:
                        predecessors.add(pred_id)
    
    return predecessors


def _resolve_same_task_vertical_dependencies(
    base_task: BaseTask,
    task_id: str,
    zone: str,
    floor: int,
    task_id_registry: Set[str]
) -> Set[str]:
    """Resolve same-task vertical dependencies (previous floors)"""
    predecessors = set()
    
    if (floor > 0 and 
        getattr(base_task, "cross_floor_repetition", True) and 
        getattr(base_task, "vertical_workflow", True)):
        
        prev_floor_task = f"{base_task.id}-F{floor-1}-{zone}"
        if prev_floor_task in task_id_registry:
            predecessors.add(prev_floor_task)
    
    return predecessors


def _resolve_cross_zone_dependencies(
    base_task: BaseTask,
    task_id: str,
    zone: str,
    floor: int,
    group_idx: int,
    strategy_type: str,
    zone_groups: List[List[str]],
    task_id_registry: Set[str]
) -> Set[str]:
    """Resolve cross-zone sequencing dependencies"""
    predecessors = set()
    
    if group_idx > 0 and strategy_type == "group_sequential":
        prev_group = zone_groups[group_idx - 1]
        for prev_zone in prev_group:
            cross_zone_task = f"{base_task.id}-F{floor}-{prev_zone}"
            if cross_zone_task in task_id_registry:
                predecessors.add(cross_zone_task)
    
    return predecessors


def _resolve_user_custom_dependencies(
    base_task: BaseTask,
    zone: str,
    floor: int,
    task_id_registry: Set[str]
) -> Set[str]:
    """Resolve user-configured custom dependencies"""
    predecessors = set()
    
    # Check for user-defined custom dependencies
    custom_deps = getattr(base_task, 'custom_dependencies', [])
    for custom_dep in custom_deps:
        if _is_custom_dependency_valid(custom_dep, zone, floor, task_id_registry):
            predecessors.add(custom_dep['target_task'])
    
    return predecessors


def _is_custom_dependency_valid(custom_dep: Dict, zone: str, floor: int, task_id_registry: Set[str]) -> bool:
    """Validate if a custom dependency applies to this task/floor/zone"""
    # Check zone matching
    if 'zones' in custom_dep and zone not in custom_dep['zones']:
        return False
    
    # Check floor range
    if 'floor_range' in custom_dep:
        min_floor, max_floor = custom_dep['floor_range']
        if not (min_floor <= floor <= max_floor):
            return False
    
    # Check if target task exists
    if custom_dep['target_task'] not in task_id_registry:
        return False
    
    return True


def _get_predecessor_floor_optimized(predecessor_task: BaseTask, current_floor: int) -> int:
    """Optimized floor calculation for predecessors"""
    # If predecessor is ground-only, use floor 0
    if getattr(predecessor_task, 'ground_only', False):
        return 0
    
    # Use same floor by default, but allow configuration
    return getattr(predecessor_task, 'predecessor_floor_offset', 0) + current_floor


def _validate_generated_tasks(tasks: List[Task], task_id_registry: Set[str]):
    """Validate generated tasks for consistency"""
    if not tasks:
        raise ValueError("No tasks were generated")
    
    # Check for task ID uniqueness
    task_ids = set()
    for task in tasks:
        if task.id in task_ids:
            raise ValueError(f"Duplicate task ID generated: {task.id}")
        task_ids.add(task.id)
    
    # Validate that all referenced predecessors exist
    for task in tasks:
        for pred_id in task.predecessors:
            if pred_id not in task_id_registry and pred_id not in task_ids:
                logger.warning(f"⚠️ Missing predecessor reference: {pred_id} for task {task.id}")


def _count_total_dependencies(tasks: List[Task]) -> int:
    """Count total dependencies across all tasks"""
    return sum(len(task.predecessors) for task in tasks)


def generate_user_cross_floor_dependencies(
    base_task: BaseTask,
    zone: str,
    floor: int,
    task_id_registry: Set[str],
    base_by_id: Dict[str, BaseTask]
) -> List[str]:
    """
    Generate user-configured cross-floor dependencies
    
    Note: This function is maintained for backward compatibility
    """
    dependencies = []
    
    # Check for user-defined cross-floor dependencies
    user_cross_deps = getattr(base_task, 'user_cross_floor_dependencies', [])
    
    for dep_config in user_cross_deps:
        target_task_id = dep_config.get('target_task')
        target_floor_offset = dep_config.get('floor_offset', -1)  # Default: floor below
        target_zone = dep_config.get('zone', zone)  # Default: same zone
        
        target_floor = floor + target_floor_offset
        if target_floor >= 0:  # Ensure valid floor
            target_task_full_id = f"{target_task_id}-F{target_floor}-{target_zone}"
            if target_task_full_id in task_id_registry:
                dependencies.append(target_task_full_id)
    
    return dependencies


class TaskGenerationError(Exception):
    """Custom exception for task generation errors"""
    pass
