# backend/utils/email_validator.py
"""
Lightweight Email Validator - No external dependencies
Provides basic email validation without requiring external packages
"""
import re
import logging
from typing import Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EmailValidationResult:
    """Email validation result with details"""
    is_valid: bool
    normalized_email: Optional[str] = None
    error_message: Optional[str] = None

class EmailValidator:
    """
    Professional email validator with comprehensive checks
    No external dependencies required
    """
    
    # Comprehensive email regex pattern
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    )
    
    # Common disposable email domains
    DISPOSABLE_DOMAINS = {
        'tempmail.com', 'guerrillamail.com', 'mailinator.com', '10minutemail.com',
        'throwawaymail.com', 'fakeinbox.com', 'yopmail.com', 'trashmail.com',
        'disposableemail.com', 'tempmail.net', 'getairmail.com', 'tmpmail.org'
    }
    
    # Common TLDs for validation
    VALID_TLDS = {
        'com', 'org', 'net', 'edu', 'gov', 'mil', 'io', 'co', 'info', 'biz',
        'me', 'tv', 'us', 'uk', 'ca', 'de', 'fr', 'it', 'es', 'nl', 'ru', 'jp',
        'cn', 'in', 'br', 'au', 'nz', 'ch', 'se', 'no', 'dk', 'fi', 'be', 'at'
    }
    
    @classmethod
    def validate_email(cls, email: str, check_deliverability: bool = False) -> EmailValidationResult:
        """
        Validate email address with comprehensive checks
        
        Args:
            email: Email address to validate
            check_deliverability: Whether to check for disposable emails (basic)
            
        Returns:
            EmailValidationResult with validation details
        """
        if not email or not isinstance(email, str):
            return EmailValidationResult(
                is_valid=False,
                error_message="Email must be a non-empty string"
            )
        
        # Clean and normalize email
        clean_email = email.strip().lower()
        
        # Check length
        if len(clean_email) > 254:  # RFC 5321 limit
            return EmailValidationResult(
                is_valid=False,
                error_message="Email address too long (max 254 characters)"
            )
        
        # Basic format validation
        if not cls._validate_format(clean_email):
            return EmailValidationResult(
                is_valid=False,
                error_message="Invalid email format"
            )
        
        # Local part validation
        local_part, domain_part = clean_email.split('@', 1)
        local_validation = cls._validate_local_part(local_part)
        if not local_validation[0]:
            return EmailValidationResult(
                is_valid=False,
                error_message=local_validation[1]
            )
        
        # Domain validation
        domain_validation = cls._validate_domain_part(domain_part)
        if not domain_validation[0]:
            return EmailValidationResult(
                is_valid=False,
                error_message=domain_validation[1]
            )
        
        # Optional: Check for disposable emails
        if check_deliverability:
            disposable_check = cls._check_disposable_domain(domain_part)
            if not disposable_check[0]:
                return EmailValidationResult(
                    is_valid=False,
                    error_message=disposable_check[1]
                )
        
        return EmailValidationResult(
            is_valid=True,
            normalized_email=clean_email
        )
    
    @classmethod
    def _validate_format(cls, email: str) -> bool:
        """Validate email format using regex"""
        return bool(cls.EMAIL_REGEX.match(email))
    
    @classmethod
    def _validate_local_part(cls, local_part: str) -> Tuple[bool, Optional[str]]:
        """Validate local part of email (before @)"""
        # Length check
        if len(local_part) == 0:
            return False, "Local part cannot be empty"
        if len(local_part) > 64:  # RFC 5321 limit
            return False, "Local part too long (max 64 characters)"
        
        # Check for consecutive dots
        if '..' in local_part:
            return False, "Local part cannot contain consecutive dots"
        
        # Check start and end characters
        if local_part.startswith('.') or local_part.endswith('.'):
            return False, "Local part cannot start or end with a dot"
        
        # Check for valid characters (basic)
        if not re.match(r'^[a-zA-Z0-9.!#$%&''*+/=?^_`{|}~-]+$', local_part):
            return False, "Local part contains invalid characters"
        
        return True, None
    
    @classmethod
    def _validate_domain_part(cls, domain_part: str) -> Tuple[bool, Optional[str]]:
        """Validate domain part of email (after @)"""
        # Basic domain structure
        if '.' not in domain_part:
            return False, "Domain must contain a dot"
        
        parts = domain_part.split('.')
        
        # Check each part
        for part in parts:
            if len(part) == 0:
                return False, "Domain part cannot be empty"
            if len(part) > 63:  # RFC 1035 limit
                return False, f"Domain part '{part}' too long (max 63 characters)"
            if not re.match(r'^[a-zA-Z0-9-]+$', part):
                return False, f"Domain part '{part}' contains invalid characters"
            if part.startswith('-') or part.endswith('-'):
                return False, f"Domain part '{part}' cannot start or end with hyphen"
        
        # Check TLD (last part)
        tld = parts[-1].lower()
        if len(tld) < 2:
            return False, "TLD must be at least 2 characters"
        
        # Check if TLD looks reasonable (basic check)
        if not re.match(r'^[a-z]{2,}$', tld):
            return False, "Invalid TLD format"
        
        return True, None
    
    @classmethod
    def _check_disposable_domain(cls, domain: str) -> Tuple[bool, Optional[str]]:
        """Check if domain is from a disposable email service"""
        domain_lower = domain.lower()
        
        # Check exact domain match
        if domain_lower in cls.DISPOSABLE_DOMAINS:
            return False, "Disposable email addresses are not allowed"
        
        # Check subdomains of disposable services
        for disposable_domain in cls.DISPOSABLE_DOMAINS:
            if domain_lower.endswith('.' + disposable_domain):
                return False, "Disposable email addresses are not allowed"
        
        return True, None

# Backward compatibility - mimic the external library interface
def validate_email(email: str, check_deliverability: bool = False) -> EmailValidationResult:
    """
    Main validation function that mimics the external email-validator library
    
    Usage:
        try:
            result = validate_email("test@example.com")
            if result.is_valid:
                normalized_email = result.normalized_email
        except Exception as e:
            # Handle validation errors
    """
    return EmailValidator.validate_email(email, check_deliverability)

# Exception class for compatibility
class EmailNotValidError(Exception):
    """Exception raised for invalid email addresses"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)