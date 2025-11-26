"""
Enhanced User repository with complete CRUD operations
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from backend.models.db_models import UserDB, UserTaskTemplateDB

logger = logging.getLogger(__name__)

class UserRepository:
    """Enhanced User repository with complete method set"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_user_by_id(self, user_id: int) -> Optional[UserDB]:
        """Get user by ID"""
        try:
            return self.session.query(UserDB).filter(UserDB.id == user_id).first()
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[UserDB]:
        """Get user by username"""
        try:
            return self.session.query(UserDB).filter(UserDB.username == username).first()
        except Exception as e:
            logger.error(f"Failed to get user {username}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[UserDB]:
        """Get user by email address"""
        try:
            return self.session.query(UserDB).filter(UserDB.email == email).first()
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    def get_all_users(self) -> List[UserDB]:
        """Get all users (admin only)"""
        try:
            return self.session.query(UserDB).order_by(UserDB.username).all()
        except Exception as e:
            logger.error(f"Failed to get all users: {e}")
            return []
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[UserDB]:
        """Create a new user"""
        try:
            user = UserDB(**user_data)
            self.session.add(user)
            #self.session.commit()
            #self.session.refresh(user)
            self.session.flush()
            logger.info(f"User created successfully: {user_data['username']}")
            return user
        except Exception as e:
            logger.error(f"Failed to create user {user_data.get('username')}: {e}")
            #self.session.rollback()
            return None
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """Update user information"""
        try:
            user = self.session.query(UserDB).filter(UserDB.id == user_id).first()
            if not user:
                return False
            
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            #self.session.commit()
            self.session.flush() 
            return True
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            #self.session.rollback()
            return False
    
    def update_user_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            user = self.session.query(UserDB).filter(UserDB.id == user_id).first()
            if user:
                from datetime import datetime
                user.last_login = datetime.now()
                #self.session.commit()
                self.session.flush()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
            #self.session.rollback()
            return False
    
    def get_user_task_templates(self, user_id: int, discipline: str = None, 
                              active_only: bool = True) -> List[UserTaskTemplateDB]:
        """Get user task templates"""
        try:
            query = self.session.query(UserTaskTemplateDB).filter(
                UserTaskTemplateDB.user_id == user_id
            )
            
            if active_only:
                query = query.filter(UserTaskTemplateDB.is_active == True)
            
            if discipline:
                query = query.filter(UserTaskTemplateDB.discipline == discipline)
            
            return query.order_by(
                UserTaskTemplateDB.discipline, 
                UserTaskTemplateDB.name
            ).all()
            
        except Exception as e:
            logger.error(f"Failed to get user task templates: {e}")
            return []
    
    def create_user_task_template(self, template_data: Dict[str, Any]) -> Optional[UserTaskTemplateDB]:
        """Create new user task template"""
        try:
            template = UserTaskTemplateDB(**template_data)
            self.session.add(template)
            #self.session.commit()
            self.session.flush()
            return template
        except Exception as e:
            logger.error(f"Failed to create task template: {e}")
            #self.session.rollback()
            return None