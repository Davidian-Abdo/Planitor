import json
from backend.db.session import get_db_session
from backend.services.user_task_service import UserTaskService

# --- Setup DB session ---
db_session = get_db_session()

# --- Initialize service ---
task_service = UserTaskService(db_session)

# --- Load default tasks for a test user ---
user_id = 1
tasks = task_service.load_default_tasks(user_id)

print(f"✅ Loaded {len(tasks)} tasks")

# --- Step 1: Check types ---
for i, task in enumerate(tasks[:5]):  # first 5 tasks only
    print(f"\nTask {i}:")
    for k, v in task.items():
        print(f"  {k} ({type(v).__name__}) = {v}")

# --- Step 2: JSON-safe conversion test ---
errors = []
for i, task in enumerate(tasks):
    try:
        safe_task = {
            'ID': str(task.get('id', 'N/A')),
            'Nom': str(task.get('name', 'Inconnu')),
            'Corps d\'État': str(task.get('discipline', 'Général')),
            'Type Ressource': str(task.get('resource_type', 'ouvrier')),
            'Méthode Calcul': str(task.get('duration_calculation_method', 'fixed_duration')),
            'Durée Fixe (Jours)': float(task.get('base_duration', 0) or 0),
            'Durée Unitaire (J/Unité)': float(task.get('unit_duration', 0) or 0),
            'Équipes Min': int(task.get('min_crews_needed', 1) or 1),
            'Engin Min': task.get('min_equipment_needed', {}),   # dict
            'Predecessors': task.get('predecessors', []),        # list
            'Décalage': float(task.get('delay', 0) or 0),
            'Sensible Météo': bool(task.get('weather_sensitive', False)),
            'Contrôle Qualité': bool(task.get('quality_gate', False)),
            'Actif': bool(task.get('included', True)),
        }
        # Try serializing dict/list fields
        json.dumps(safe_task['Engin Min'])
        json.dumps(safe_task['Predecessors'])
    except Exception as e:
        errors.append((i, str(e)))

if errors:
    print(f"❌ JSON serialization failed for {len(errors)} tasks:")
    for idx, err in errors:
        print(f" - Task {idx}: {err}")
else:
    print("✅ All tasks are JSON-serializable and safe for the table!")