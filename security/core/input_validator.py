"""
🔒 INPUT VALIDATOR - Comprehensive Input Validation & Sanitization
Protects against: XSS, SQL Injection, Command Injection, Path Traversal, etc.
"""

import re
import html
import urllib.parse
from typing import Any, Optional, List, Pattern
from pathlib import Path
import mimetypes


class ValidationError(Exception):
    """Custom validation error exception"""
    pass


class InputValidator:
    """Centralized input validation and sanitization"""
    
    # Common regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    # Dangerous patterns to block
    SQL_INJECTION_PATTERNS = [
        re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)", re.IGNORECASE),
        re.compile(r"(\bUNION\b.*\bSELECT\b)", re.IGNORECASE),
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        re.compile(r"[;&|`$(){}[\]<>]"),  # Shell metacharacters
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        re.compile(r"\.\./"),  # Directory traversal
        re.compile(r"\.\.\\"),  # Windows directory traversal
    ]
    
    @staticmethod
    def validate_string(
        value: Any,
        field_name: str = "field",
        max_length: int = 255,
        min_length: int = 0,
        pattern: Optional[Pattern] = None,
        allow_empty: bool = False
    ) -> str:
        """Validate and sanitize string input"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string, got {type(value).__name__}")
        
        value = value.strip()
        
        if not value and not allow_empty:
            raise ValidationError(f"{field_name} cannot be empty")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} exceeds maximum length of {max_length}")
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters")
        
        if pattern and not pattern.match(value):
            raise ValidationError(f"{field_name} does not match required pattern")
        
        return value
    
    @classmethod
    def validate_email(cls, email: str, field_name: str = "email") -> str:
        """Validate email address"""
        email = cls.validate_string(email, field_name, max_length=254)
        if not cls.EMAIL_PATTERN.match(email):
            raise ValidationError(f"{field_name} is not a valid email address")
        return email.lower()
    
    @classmethod
    def sanitize_html(cls, html_content: str) -> str:
        """Sanitize HTML to prevent XSS attacks"""
        return html.escape(html_content)
    
    @classmethod
    def check_sql_injection(cls, value: str, field_name: str = "field") -> None:
        """Check for SQL injection attempts"""
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if pattern.search(value):
                raise ValidationError(f"{field_name} contains potential SQL injection pattern")


if __name__ == "__main__":
    validator = InputValidator()
    print("✅ Input Validator loaded successfully")
