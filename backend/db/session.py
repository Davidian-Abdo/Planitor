"""
PROFESSIONAL Database Session Management
Enhanced with transaction control for Streamlit architecture
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration for production"""
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'Planitor_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'ABDOABDO')
    
    @property
    def DATABASE_URL(self):
        """Production database URL"""
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

def create_engine_production():
    """Create production-ready database engine"""
    config = DatabaseConfig()
    
    logger.info(f"🔗 Connecting to PostgreSQL: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    
    engine = create_engine(
        config.DATABASE_URL,
        poolclass=QueuePool,
        echo=False,
        pool_pre_ping=True,
        max_overflow=10,
        pool_size=5,
    )
    
    # Test connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Production database engine created successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    return engine

# Create engine and session factory
engine = create_engine_production()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI-style database dependency
    Use with: db = next(get_db())
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """
    Traditional session getter for backward compatibility
    Returns SQLAlchemy session for manual transaction management
    """
    return SessionLocal()

def safe_commit(db_session, operation_name="Operation"):
    """
    Professional safe commit with comprehensive error handling
    Args:
        db_session: SQLAlchemy session instance
        operation_name: Name of operation for logging
    Returns:
        bool: True if commit successful, False otherwise
    """
    try:
        db_session.commit()
        logger.info(f"✅ {operation_name} committed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ {operation_name} commit failed: {e}")
        try:
            db_session.rollback()
            logger.info(f"🔄 Rollback executed after failed commit for {operation_name}")
        except Exception as rollback_error:
            logger.error(f"❌ Rollback also failed: {rollback_error}")
        return False

def safe_rollback(db_session, operation_name="Operation"):
    """
    Professional safe rollback with comprehensive error handling
    Args:
        db_session: SQLAlchemy session instance
        operation_name: Name of operation for logging
    Returns:
        bool: True if rollback successful, False otherwise
    """
    try:
        db_session.rollback()
        logger.info(f"🔄 {operation_name} rolled back successfully")
        return True
    except Exception as e:
        logger.error(f"❌ {operation_name} rollback failed: {e}")
        return False

def init_database():
    """
    Smart database initialization - only creates tables if they don't exist
    Returns:
        bool: True if initialization successful
    """
    try:
        from backend.models.db_models import UserDB
        with engine.connect() as conn:
            try:
                # Try to query users table - if it works, tables exist
                conn.execute(text("SELECT 1 FROM users LIMIT 1"))
                logger.info("✅ Database tables already exist - skipping creation")
                return True
            except:
                # Tables don't exist, create them
                logger.info("🔄 Creating database tables...")
                from backend.db.base import Base
                import backend.models.db_models  # This registers all models
                Base.metadata.create_all(bind=engine)
                logger.info("✅ Database tables created successfully")
                return True
                
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

def close_database():
    """Cleanup database connections"""
    engine.dispose()
    logger.info("✅ Database connections closed")

def get_database_stats():
    """Get database health metrics"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.scalar()
            
            return {
                'status': 'connected',
                'version': version.split(',')[0],
                'database': db_name,
                'table_count': table_count
            }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

# Repository factory functions
def get_user_repository(db_session):
    """Get user repository instance"""
    from backend.db.repositories.user_repo import UserRepository
    return UserRepository(db_session)

def get_project_repository(db_session):
    """Get project repository instance"""
    from backend.db.repositories.project_repo import ProjectRepository
    return ProjectRepository(db_session)

def get_schedule_repository(db_session):
    """Get schedule repository instance"""
    from backend.db.repositories.schedule_repo import ScheduleRepository
    return ScheduleRepository(db_session)

def get_task_repository(db_session):
    """Get task repository instance"""
    from backend.db.repositories.task_repo import TaskRepository
    return TaskRepository(db_session)

def get_progress_repository(db_session):
    """Get progress repository instance"""
    from backend.db.repositories.progress_repo import ProgressRepository
    return ProgressRepository(db_session)

def get_resource_repository(db_session):
    """Get resource repository instance"""
    from backend.db.repositories.resource_repo import ResourceRepository
    return ResourceRepository(db_session)

def get_report_repository(db_session):
    """Get report repository instance"""
    from backend.db.repositories.report_repo import ReportRepository
    return ReportRepository(db_session)