"""
Task generator that expands base tasks into per-zone/per-floor tasks
Respects discipline-level zone sequencing:
- `discipline_zone_cfg` is a dict: discipline -> list of groups (each group is list of zone names)
- Floors are passed as `zones_floors` mapping: { "Zone A": 5, "Zone B": 3 }
- Task ID format used: "{zone}-{discipline_short}-F{floor}-{counter:03d}"
- Dependency rule: tasks in group N+1 depend on all tasks in group N (strong enforcement)
"""
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime

from backend.models.domain_models import Task, BaseTask, TaskType, TaskStatus

logger = logging.getLogger(__name__)


def _discipline_short(discipline: str) -> str:
    """Create a short code for the discipline to use in IDs. Keep alphanumeric only and uppercase."""
    clean = "".join(c for c in discipline if c.isalnum())
    return (clean[:4] or discipline).upper()


def generate_tasks(
    base_tasks_dict: Dict[str, BaseTask],
    zones_floors: Dict[str, int],
    cross_floor_links: Optional[Dict[str, List[str]]] = None,
    ground_disciplines: Optional[Set[str]] = None,
    discipline_zone_cfg: Optional[Dict[str, List[List[str]]]] = None,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None
) -> List[Task]:
    """
    Expand base_tasks into concrete Task objects for each zone and floor.

    Arguments
    ---------
    base_tasks_dict: mapping from base_task_id -> BaseTask
    zones_floors: mapping zone_name -> max_floor (integer)
    discipline_zone_cfg: mapping discipline -> list of zone-groups (each group is list of zone names)
                         If absent, default is one group containing all zones (fully parallel).
    """
    cross_floor_links = cross_floor_links or {}
    ground_disciplines = ground_disciplines or set()
    discipline_zone_cfg = discipline_zone_cfg or {}

    # Build registry to validate existence of generated ids quickly
    task_ids_registry = set()

    # We'll generate tasks and collect them; then compute dependencies including group sequencing
    tasks: List[Task] = []

    # counters per (zone, discipline, floor) to make unique suffix
    counters: Dict[Tuple[str, str, int], int] = {}

    # Precompute discipline short forms
    discipline_short_map = {}

    for base_id, base_task in base_tasks_dict.items():
        discipline_short_map.setdefault(base_task.discipline, _discipline_short(base_task.discipline))

    # Build initial task placeholders and ID registry
    for base_id, base_task in base_tasks_dict.items():
        if not getattr(base_task, "included", True):
            continue

        discipline = base_task.discipline
        groups = discipline_zone_cfg.get(discipline, [list(zones_floors.keys())])  # default: all zones parallel

        for group in groups:
            # group is list of zone names
            for zone in group:
                if zone not in zones_floors:
                    logger.warning(f"Zone '{zone}' referenced in discipline cfg but not in zones_floors - skipping")
                    continue
                max_floor = zones_floors[zone]
                # decide floors
                if getattr(base_task, "repeat_on_floor", True):
                    floor_range = list(range(0, max_floor + 1))
                else:
                    floor_range = [0]

                for floor in floor_range:
                    key = (zone, discipline_short_map[discipline], floor)
                    counters[key] = counters.get(key, 0) + 1
                    counter = counters[key]

                    task_id = f"{zone}-{discipline_short_map[discipline]}-F{floor}-{counter:03d}"
                    task_ids_registry.add(task_id)

                    # create task object without predecessors yet
                    t = Task(
                        id=task_id,
                        base_id=base_id,
                        name=base_task.name,
                        base_duration=base_task.base_duration,
                        discipline=discipline,
                        sub_discipline=getattr(base_task, "sub_discipline", "General"),
                        zone=zone,
                        floor=floor,
                        resource_type=base_task.resource_type,
                        task_type=base_task.task_type if isinstance(base_task.task_type, TaskType) else TaskType[base_task.task_type.upper()] if isinstance(base_task.task_type, str) else TaskType.WORKER,
                        min_crews_needed=getattr(base_task, "min_crews_needed", 1),
                        min_equipment_needed=getattr(base_task, "min_equipment_needed", {}) or {},
                        predecessors=[],  # fill later
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
                    tasks.append(t)

    # Helper to find generated task_id for a base_task id in a given zone/floor
    def gen_task_id_for(base_id: str, zone: str, floor: int, discipline_short: str) -> Optional[str]:
        # We will attempt to find any generated id that starts with pattern base identification:
        # Because multiple base IDs could map to same base_id prefix, we search in registry for an id that contains base_id
        # Safer: map base_id to generated tasks: we can scan tasks for matching base_id, zone, floor
        for t in tasks:
            if t.base_id == base_id and t.zone == zone and t.floor == floor:
                return t.id
        return None

    # Build a lookup for tasks by (base_id, zone, floor)
    tasks_by_triplet = {}
    for t in tasks:
        tasks_by_triplet[(t.base_id, t.zone, t.floor)] = t

    # Now compute predecessors for each generated task
    # Precedence rules (applied in order):
    # 1) Base task's declared predecessors -> same zone/same floor by default (or with offsets)
    # 2) cross_floor_links -> apply if declared in cross_floor_links mapping
    # 3) same-task vertical dependency (previous floor) if base_task specifies cross_floor_repetition/vertical_workflow
    # 4) cross-zone dependencies from discipline groups (rule A): tasks in group N+1 depend on ALL tasks of group N
    # 5) custom user-defined dependencies if any (custom_dependencies field)
    base_by_id = {bid: b for bid, b in base_tasks_dict.items()}

    # Build mapping discipline -> groups (sequence)
    discipline_groups_map = {}
    for disc, groups in discipline_zone_cfg.items():
        discipline_groups_map[disc] = groups

    # Build reverse lookup: zone -> group index per discipline
    zone_group_index = {}  # (discipline, zone) -> group_idx
    for disc, groups in discipline_groups_map.items():
        for gi, group in enumerate(groups):
            for z in group:
                zone_group_index[(disc, z)] = gi

    # Compute predecessors
    for t in tasks:
        base_task = base_by_id.get(t.base_id)
        if not base_task:
            continue

        preds = set()

        # 1) Regular declared predecessors (same zone, same floor)
        for pred_base in getattr(base_task, "predecessors", []) or []:
            # find pred for same zone & floor (apply predecessor floor offset if present)
            pred_floor = getattr(base_by_id.get(pred_base, {}), "predecessor_floor_offset", 0) + t.floor
            if pred_floor < 0:
                continue
            cand = tasks_by_triplet.get((pred_base, t.zone, pred_floor))
            if cand:
                preds.add(cand.id)

        # 2) cross_floor_links (if base_task.id in cross_floor_links)
        if t.base_id in (cross_floor_links or {}):
            for pred_base in (cross_floor_links or {}).get(t.base_id, []):
                pred_floor = t.floor - 1
                if pred_floor >= 0:
                    cand = tasks_by_triplet.get((pred_base, t.zone, pred_floor))
                    if cand:
                        preds.add(cand.id)

        # 3) same-task vertical dependency (previous floor)
        if t.floor > 0 and getattr(base_task, "vertical_workflow", True) and getattr(base_task, "cross_floor_repetition", True):
            prev = tasks_by_triplet.get((t.base_id, t.zone, t.floor - 1))
            if prev:
                preds.add(prev.id)

        # 4) discipline group sequencing (Rule A: group N+1 depends on ALL tasks in group N)
        # Determine group index for this t.zone under t.discipline
        gi = zone_group_index.get((t.discipline, t.zone), None)
        if gi is not None and gi > 0:
            prev_group = discipline_groups_map.get(t.discipline, [])[gi - 1]
            # for every base task in previous group: add predecessor for same base task and same floor
            for prev_zone in prev_group:
                cand = tasks_by_triplet.get((t.base_id, prev_zone, t.floor))
                if cand:
                    preds.add(cand.id)

        # 5) custom user-defined cross-zone or cross-floor dependencies if present on base_task.custom_dependencies
        for custom in getattr(base_task, "custom_dependencies", []) or []:
            # expected custom format: {'target_task': 'BASEID', 'zones': [...], 'floor_range': [min,max], 'zone': 'Zone X'...}
            try:
                target = custom.get("target_task")
                target_zone = custom.get("zone", t.zone)
                if "floor_range" in custom:
                    minf, maxf = custom["floor_range"]
                    if not (minf <= t.floor <= maxf):
                        continue
                cand = tasks_by_triplet.get((target, target_zone, t.floor))
                if cand:
                    preds.add(cand.id)
            except Exception:
                continue

        # Remove self references
        preds.discard(t.id)
        t.predecessors = sorted(list(preds))

    logger.info(f"Generated {len(tasks)} tasks with discipline sequencing applied")
    return tasks