from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# ✅ CORRECT PATH CALCULATION for env.py in migrations folder
# env.py is at: backend/db/migrations/env.py
current_file = os.path.abspath(__file__)  # backend/db/migrations/env.py
migrations_dir = os.path.dirname(current_file)  # backend/db/migrations
db_dir = os.path.dirname(migrations_dir)  # backend/db  
backend_dir = os.path.dirname(db_dir)  # backend
project_root = os.path.dirname(backend_dir)  # project root

# Add project root to Python path
sys.path.insert(0, project_root)

print(f"🔧 Alembic Path Debug:")
print(f"  env.py location: {current_file}")
print(f"  Project root: {project_root}")
print(f"  Python path: {sys.path}")

# Import from our SINGLE source of truth
from backend.db.base import Base
import backend.models.db_models  # This registers all models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # Use our production engine
    from backend.db.session import engine
    
    with engine.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()