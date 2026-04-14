"""
Tests for security/core/audit_logger.py
Covers: enums, log entry creation, event logging, convenience methods.
"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from security.core.audit_logger import (
    AuditLogger,
    SecurityEventType,
    SeverityLevel,
)


# ---------------------------------------------------------------------------
# Enum values
# ---------------------------------------------------------------------------

class TestEnums:
    """Tests for SecurityEventType and SeverityLevel enums"""

    def test_security_event_types(self):
        assert SecurityEventType.LOGIN_SUCCESS.value == "login_success"
        assert SecurityEventType.LOGIN_FAILURE.value == "login_failure"
        assert SecurityEventType.ACCESS_DENIED.value == "access_denied"
        assert SecurityEventType.RATE_LIMIT_EXCEEDED.value == "rate_limit_exceeded"
        assert SecurityEventType.TRADE_EXECUTED.value == "trade_executed"
        assert SecurityEventType.EMERGENCY_SHUTDOWN.value == "emergency_shutdown"

    def test_severity_levels(self):
        assert SeverityLevel.DEBUG.value == "debug"
        assert SeverityLevel.INFO.value == "info"
        assert SeverityLevel.WARNING.value == "warning"
        assert SeverityLevel.ERROR.value == "error"
        assert SeverityLevel.CRITICAL.value == "critical"


# ---------------------------------------------------------------------------
# Log entry creation
# ---------------------------------------------------------------------------

class TestLogEntryCreation:
    """Tests for AuditLogger._create_log_entry"""

    def setup_method(self):
        self.logger = AuditLogger(
            log_dir=Path("/tmp/test_audit_logs"),
            app_name="test_app",
            enable_console=False,
        )

    def test_basic_entry(self):
        entry = self.logger._create_log_entry(
            SecurityEventType.LOGIN_SUCCESS,
            SeverityLevel.INFO,
            "User logged in",
        )
        assert entry['event_type'] == "login_success"
        assert entry['severity'] == "info"
        assert entry['message'] == "User logged in"
        assert entry['app'] == "test_app"
        assert 'timestamp' in entry

    def test_entry_with_user_id(self):
        entry = self.logger._create_log_entry(
            SecurityEventType.DATA_READ,
            SeverityLevel.INFO,
            "Data read",
            user_id="user123",
        )
        assert entry['user_id'] == "user123"
        assert 'user_id_hash' in entry
        assert len(entry['user_id_hash']) == 16

    def test_entry_with_ip_address(self):
        entry = self.logger._create_log_entry(
            SecurityEventType.LOGIN_SUCCESS,
            SeverityLevel.INFO,
            "Login",
            ip_address="192.168.1.1",
        )
        assert entry['ip_address'] == "192.168.1.1"
        assert 'ip_hash' in entry

    def test_entry_with_details(self):
        entry = self.logger._create_log_entry(
            SecurityEventType.CONFIG_CHANGED,
            SeverityLevel.INFO,
            "Config changed",
            details={"key": "debug_mode", "new": True},
        )
        assert entry['details']['key'] == "debug_mode"

    def test_entry_without_optional_fields(self):
        entry = self.logger._create_log_entry(
            SecurityEventType.DATA_READ,
            SeverityLevel.DEBUG,
            "Read",
        )
        assert 'user_id' not in entry
        assert 'ip_address' not in entry
        assert 'details' not in entry


# ---------------------------------------------------------------------------
# Event logging
# ---------------------------------------------------------------------------

class TestEventLogging:
    """Tests for log_event and convenience methods"""

    def setup_method(self):
        self.logger = AuditLogger(
            log_dir=Path("/tmp/test_audit_event_logs"),
            app_name="test_events",
            enable_console=False,
        )

    def test_log_event_no_exception(self):
        """log_event should run without errors"""
        self.logger.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            "Test login",
            SeverityLevel.INFO,
            user_id="user1",
            ip_address="10.0.0.1",
        )

    def test_log_login_success(self):
        self.logger.log_login_success("admin", "10.0.0.1", method="password")

    def test_log_login_failure(self):
        self.logger.log_login_failure("admin", "10.0.0.1", "bad password")

    def test_log_access_denied(self):
        self.logger.log_access_denied("user1", "/admin", "write")

    def test_log_sensitive_data_access(self):
        self.logger.log_sensitive_data_access("user1", "api_keys")

    def test_log_config_change(self):
        self.logger.log_config_change("admin", "debug", False, True)

    def test_log_rate_limit_exceeded(self):
        self.logger.log_rate_limit_exceeded("10.0.0.2", "10.0.0.2", "100/min")

    def test_log_suspicious_activity(self):
        self.logger.log_suspicious_activity("user2", "10.0.0.3", "Port scanning")

    def test_log_security_violation(self):
        self.logger.log_security_violation("injection", "SQL injection detected")

    def test_log_trade_executed(self):
        self.logger.log_trade_executed("trader1", "BTC/USDT", "buy", 0.5, 45000.0)

    def test_log_circuit_breaker(self):
        self.logger.log_circuit_breaker_triggered("loss limit", "10%")

    def test_log_emergency_shutdown(self):
        self.logger.log_emergency_shutdown("manual trigger")


# ---------------------------------------------------------------------------
# Log file creation
# ---------------------------------------------------------------------------

class TestLogFiles:
    """Tests for log file creation"""

    def test_creates_log_directory(self, tmp_path):
        log_dir = tmp_path / "new_logs"
        logger = AuditLogger(log_dir=log_dir, app_name="test", enable_console=False)
        assert log_dir.exists()

    def test_writes_to_log_file(self, tmp_path):
        log_dir = tmp_path / "file_logs"
        logger = AuditLogger(log_dir=log_dir, app_name="test_write", enable_console=False)
        logger.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            "test message",
            SeverityLevel.INFO,
        )

        # Check that a log file was created
        log_files = list(log_dir.glob("audit_*.log"))
        assert len(log_files) >= 1

        # Check content is valid JSON
        content = log_files[0].read_text().strip()
        if content:
            entry = json.loads(content)
            assert entry['event_type'] == 'login_success'
