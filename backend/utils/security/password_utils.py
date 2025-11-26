"""
Password hashing and verification utilities using bcrypt
"""
import bcrypt
import logging
from typing import Union

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with salt
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    try:
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return hashed.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password to verify
        hashed_password: Hashed password to verify against
        
    Returns:
        bool: True if password matches hash
    """
    try:
        if not password or not hashed_password:
            return False
        
        # Verify password
        is_valid = bcrypt.checkpw(
            password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def generate_secure_password(length: int = 12) -> str:
    """
    Generate a secure random password
    
    Args:
        length: Length of password to generate
        
    Returns:
        Secure random password
    """
    import secrets
    import string
    
    try:
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")
        
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill remaining length with random choices from all sets
        all_chars = lowercase + uppercase + digits + special
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # Shuffle the password characters
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
        
    except Exception as e:
        logger.error(f"Error generating secure password: {e}")
        raise

def validate_password_complexity(password: str) -> dict:
    """
    Validate password complexity requirements
    
    Args:
        password: Password to validate
        
    Returns:
        Dict with validation results
    """
    import re
    
    result = {
        'is_valid': True,
        'checks': {
            'length': False,
            'lowercase': False,
            'uppercase': False,
            'digit': False,
            'special': False
        },
        'score': 0,
        'feedback': []
    }
    
    # Check length (minimum 8 characters)
    if len(password) >= 8:
        result['checks']['length'] = True
        result['score'] += 1
    else:
        result['feedback'].append("Le mot de passe doit contenir au moins 8 caractères")
    
    # Check for lowercase letters
    if re.search(r'[a-z]', password):
        result['checks']['lowercase'] = True
        result['score'] += 1
    else:
        result['feedback'].append("Le mot de passe doit contenir au moins une lettre minuscule")
    
    # Check for uppercase letters
    if re.search(r'[A-Z]', password):
        result['checks']['uppercase'] = True
        result['score'] += 1
    else:
        result['feedback'].append("Le mot de passe doit contenir au moins une lettre majuscule")
    
    # Check for digits
    if re.search(r'\d', password):
        result['checks']['digit'] = True
        result['score'] += 1
    else:
        result['feedback'].append("Le mot de passe doit contenir au moins un chiffre")
    
    # Check for special characters
    if re.search(r'[!@#$%^&*()_+\-=\[\]{};:,.<>?]', password):
        result['checks']['special'] = True
        result['score'] += 1
    else:
        result['feedback'].append("Le mot de passe doit contenir au moins un caractère spécial")
    
    # Determine if overall password is valid
    result['is_valid'] = all(result['checks'].values())
    
    # Add strength rating
    if result['score'] >= 4:
        result['strength'] = 'strong'
    elif result['score'] >= 3:
        result['strength'] = 'medium'
    else:
        result['strength'] = 'weak'
    
    return result