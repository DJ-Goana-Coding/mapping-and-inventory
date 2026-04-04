"""
🔒 AUDIT LOGGER - Comprehensive Security Event Logging
Logs: Authentication, authorization, data access, configuration changes
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from enum import Enum


class SecurityEventType(Enum):
    """Types of security events"""
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    
    # Authorization
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGED = "permission_changed"
    
    # Data Access
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"
    
    # Configuration
    CONFIG_CHANGED = "config_changed"
    SECRET_ACCESSED = "secret_accessed"
    SECRET_ROTATED = "secret_rotated"
    
    # Security
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_VIOLATION = "security_violation"
    INTRUSION_ATTEMPT = "intrusion_attempt"
    
    # Trading (specific to this system)
    TRADE_EXECUTED = "trade_executed"
    CIRCUIT_BREAKER_TRIGGERED = "circuit_breaker_triggered"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"


class SeverityLevel(Enum):
    """Severity levels for events"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLogger:
    """
    Comprehensive audit logging for security events
    Logs are structured JSON for easy parsing and analysis
    """
    
    def __init__(
        self,
        log_dir: Path = Path("data/logs/security"),
        app_name: str = "citadel",
        enable_console: bool = True
    ):
        """
        Initialize audit logger
        
        Args:
            log_dir: Directory for log files
            app_name: Application name
            enable_console: Whether to also log to console
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.app_name = app_name
        
        # Set up file logger
        self.logger = logging.getLogger(f"audit_{app_name}")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # File handler with daily rotation
        log_file = self.log_dir / f"audit_{datetime.utcnow().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # JSON formatter
        json_formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(json_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler (optional)
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(json_formatter)
            self.logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _create_log_entry(
        self,
        event_type: SecurityEventType,
        severity: SeverityLevel,
        message: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create structured log entry"""
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'app': self.app_name,
            'event_type': event_type.value,
            'severity': severity.value,
            'message': message,
        }
        
        if user_id:
            entry['user_id'] = user_id
            # Hash user_id for privacy in some logs
            entry['user_id_hash'] = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        
        if ip_address:
            entry['ip_address'] = ip_address
            # Hash IP for privacy
            entry['ip_hash'] = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
        
        if details:
            entry['details'] = details
        
        return entry
    
    def log_event(
        self,
        event_type: SecurityEventType,
        message: str,
        severity: SeverityLevel = SeverityLevel.INFO,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **details
    ) -> None:
        """
        Log a security event
        
        Args:
            event_type: Type of security event
            message: Human-readable message
            severity: Severity level
            user_id: User identifier
            ip_address: IP address
            **details: Additional event details
        """
        entry = self._create_log_entry(
            event_type, severity, message, user_id, ip_address, details
        )
        
        # Convert to JSON
        log_line = json.dumps(entry)
        
        # Log at appropriate level
        if severity == SeverityLevel.DEBUG:
            self.logger.debug(log_line)
        elif severity == SeverityLevel.INFO:
            self.logger.info(log_line)
        elif severity == SeverityLevel.WARNING:
            self.logger.warning(log_line)
        elif severity == SeverityLevel.ERROR:
            self.logger.error(log_line)
        elif severity == SeverityLevel.CRITICAL:
            self.logger.critical(log_line)
    
    # Convenience methods for common events
    
    def log_login_success(self, user_id: str, ip_address: str, **details):
        """Log successful login"""
        self.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            f"User {user_id} logged in successfully",
            SeverityLevel.INFO,
            user_id=user_id,
            ip_address=ip_address,
            **details
        )
    
    def log_login_failure(self, user_id: str, ip_address: str, reason: str, **details):
        """Log failed login attempt"""
        self.log_event(
            SecurityEventType.LOGIN_FAILURE,
            f"Login failed for user {user_id}: {reason}",
            SeverityLevel.WARNING,
            user_id=user_id,
            ip_address=ip_address,
            reason=reason,
            **details
        )
    
    def log_access_denied(self, user_id: str, resource: str, action: str, **details):
        """Log access denial"""
        self.log_event(
            SecurityEventType.ACCESS_DENIED,
            f"Access denied: {user_id} attempted {action} on {resource}",
            SeverityLevel.WARNING,
            user_id=user_id,
            resource=resource,
            action=action,
            **details
        )
    
    def log_sensitive_data_access(self, user_id: str, data_type: str, **details):
        """Log access to sensitive data"""
        self.log_event(
            SecurityEventType.SENSITIVE_DATA_ACCESS,
            f"User {user_id} accessed sensitive data: {data_type}",
            SeverityLevel.INFO,
            user_id=user_id,
            data_type=data_type,
            **details
        )
    
    def log_config_change(self, user_id: str, config_key: str, old_value: Any, new_value: Any, **details):
        """Log configuration change"""
        self.log_event(
            SecurityEventType.CONFIG_CHANGED,
            f"Configuration changed: {config_key}",
            SeverityLevel.INFO,
            user_id=user_id,
            config_key=config_key,
            old_value=str(old_value),
            new_value=str(new_value),
            **details
        )
    
    def log_rate_limit_exceeded(self, identifier: str, ip_address: str, limit: str, **details):
        """Log rate limit exceeded"""
        self.log_event(
            SecurityEventType.RATE_LIMIT_EXCEEDED,
            f"Rate limit exceeded for {identifier}: {limit}",
            SeverityLevel.WARNING,
            ip_address=ip_address,
            identifier=identifier,
            limit=limit,
            **details
        )
    
    def log_suspicious_activity(self, user_id: str, ip_address: str, description: str, **details):
        """Log suspicious activity"""
        self.log_event(
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            f"Suspicious activity detected: {description}",
            SeverityLevel.ERROR,
            user_id=user_id,
            ip_address=ip_address,
            description=description,
            **details
        )
    
    def log_security_violation(self, violation_type: str, description: str, **details):
        """Log security violation"""
        self.log_event(
            SecurityEventType.SECURITY_VIOLATION,
            f"Security violation: {violation_type} - {description}",
            SeverityLevel.CRITICAL,
            violation_type=violation_type,
            description=description,
            **details
        )
    
    # Trading-specific events
    
    def log_trade_executed(
        self,
        user_id: str,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        **details
    ):
        """Log trade execution"""
        self.log_event(
            SecurityEventType.TRADE_EXECUTED,
            f"Trade executed: {side} {amount} {symbol} @ {price}",
            SeverityLevel.INFO,
            user_id=user_id,
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
            **details
        )
    
    def log_circuit_breaker_triggered(self, reason: str, threshold: str, **details):
        """Log circuit breaker trigger"""
        self.log_event(
            SecurityEventType.CIRCUIT_BREAKER_TRIGGERED,
            f"Circuit breaker triggered: {reason} (threshold: {threshold})",
            SeverityLevel.CRITICAL,
            reason=reason,
            threshold=threshold,
            **details
        )
    
    def log_emergency_shutdown(self, reason: str, **details):
        """Log emergency shutdown"""
        self.log_event(
            SecurityEventType.EMERGENCY_SHUTDOWN,
            f"Emergency shutdown initiated: {reason}",
            SeverityLevel.CRITICAL,
            reason=reason,
            **details
        )


if __name__ == "__main__":
    # Example usage
    logger = AuditLogger(app_name="citadel_test")
    
    print("🔒 Audit Logger Test\n")
    
    # Log various events
    logger.log_login_success("user123", "192.168.1.1", method="password")
    logger.log_login_failure("user456", "192.168.1.2", "invalid_password", attempts=3)
    logger.log_access_denied("user123", "/admin/config", "write")
    logger.log_sensitive_data_access("user123", "api_keys", count=5)
    logger.log_rate_limit_exceeded("192.168.1.3", "192.168.1.3", "100/minute")
    logger.log_suspicious_activity("user789", "10.0.0.1", "Multiple failed login attempts", attempts=10)
    logger.log_trade_executed("trader1", "BTC/USDT", "buy", 0.1, 45000.0, exchange="MEXC")
    logger.log_circuit_breaker_triggered("Daily loss limit", "10%", current_loss="11.5%")
    
    print("\n✅ All events logged to:", logger.log_dir)
