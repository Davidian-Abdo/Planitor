import os
import sys

print("🔧 PATH DEBUGGING")
print("=" * 50)

# Current file location
current_file = __file__
print(f"Current file: {current_file}")
print(f"File absolute path: {os.path.abspath(current_file)}")

# Calculate project root step by step
dir1 = os.path.dirname(os.path.abspath(current_file))
print(f"Level 1 (db folder): {dir1}")

dir2 = os.path.dirname(dir1)
print(f"Level 2 (backend folder): {dir2}")

dir3 = os.path.dirname(dir2)
print(f"Level 3 (project root): {dir3}")

# Test the path we're adding
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(current_file))))
print(f"Calculated project root: {project_root}")

# Add to path
sys.path.insert(0, project_root)
print(f"Python path after: {sys.path}")

# Test imports
print("\n🧪 TESTING IMPORTS:")
try:
    from backend.db.base import Base
    print("✅ backend.db.base import SUCCESS")
except Exception as e:
    print(f"❌ backend.db.base import FAILED: {e}")

try:
    import backend.models.db_models
    print("✅ backend.models.db_models import SUCCESS")
except Exception as e:
    print(f"❌ backend.models.db_models import FAILED: {e}")

# Check if backend folder exists
backend_path = os.path.join(project_root, 'backend')
print(f"\n📁 Backend folder exists: {os.path.exists(backend_path)}")
if os.path.exists(backend_path):
    print(f"Backend folder contents: {os.listdir(backend_path)}")