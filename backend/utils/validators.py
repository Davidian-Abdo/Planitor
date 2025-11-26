# backend/core/validator.py
"""
Centralized Input Validation System
"""
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError

class Validator:
    """Professional input validation with consistent patterns"""
    
    @staticmethod
    def validate_project_data(project_data: Dict) -> Tuple[bool, List[str]]:
        """Validate project creation/update data"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'start_date']
        for field in required_fields:
            if not project_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Name validation
        name = project_data.get('name', '')
        if name and (len(name) < 2 or len(name) > 200):
            errors.append("Project name must be between 2 and 200 characters")
        
        # Date validation
        start_date = project_data.get('start_date')
        if start_date:
            if isinstance(start_date, str):
                try:
                    datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                except ValueError:
                    errors.append("Invalid start date format")
            elif isinstance(start_date, (datetime, date)):
                if start_date < date.today():
                    errors.append("Start date cannot be in the past")
        
        # Zones validation
        zones = project_data.get('zones', {})
        if not isinstance(zones, dict):
            errors.append("Zones must be a dictionary")
        else:
            for zone_name, zone_config in zones.items():
                zone_errors = Validator._validate_zone_config(zone_name, zone_config)
                errors.extend(zone_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_zone_config(zone_name: str, zone_config: Dict) -> List[str]:
        """Validate individual zone configuration"""
        errors = []
        
        if not isinstance(zone_name, str) or not zone_name.strip():
            errors.append("Zone name must be a non-empty string")
        
        if not isinstance(zone_config, dict):
            errors.append(f"Zone {zone_name} configuration must be a dictionary")
            return errors
        
        # Validate max_floors
        max_floors = zone_config.get('max_floors')
        if not isinstance(max_floors, int) or max_floors < 1:
            errors.append(f"Zone {zone_name}: max_floors must be positive integer")
        
        # Validate sequence
        sequence = zone_config.get('sequence', 1)
        if not isinstance(sequence, int) or sequence < 1:
            errors.append(f"Zone {zone_name}: sequence must be positive integer")
        
        return errors
    
    @staticmethod
    def validate_user_data(user_data: Dict, is_update: bool = False) -> Tuple[bool, List[str]]:
        """Validate user registration/update data"""
        errors = []
        
        if not is_update:
            # Registration validation
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if not user_data.get(field):
                    errors.append(f"Missing required field: {field}")
        
        # Username validation
        username = user_data.get('username')
        if username:
            if len(username) < 3 or len(username) > 50:
                errors.append("Username must be between 3 and 50 characters")
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                errors.append("Username can only contain letters, numbers, and underscores")
        
        # Email validation
        email = user_data.get('email')
        if email:
            try:
                validate_email(email)
            except EmailNotValidError as e:
                errors.append(str(e))
        
        # Password validation (only for new users or password changes)
        password = user_data.get('password')
        if password and not is_update:
            password_errors = Validator._validate_password(password)
            errors.extend(password_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_password(password: str) -> List[str]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return errors