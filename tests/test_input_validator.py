"""
Tests for security/core/input_validator.py
Covers: string validation, email validation, HTML sanitization, SQL injection detection.
"""

import re
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from security.core.input_validator import InputValidator, ValidationError


# ---------------------------------------------------------------------------
# validate_string
# ---------------------------------------------------------------------------

class TestValidateString:
    """Tests for InputValidator.validate_string"""

    def test_valid_string(self):
        result = InputValidator.validate_string("hello world", "name")
        assert result == "hello world"

    def test_strips_whitespace(self):
        result = InputValidator.validate_string("  hello  ", "name")
        assert result == "hello"

    def test_rejects_non_string(self):
        with pytest.raises(ValidationError, match="must be a string"):
            InputValidator.validate_string(123, "age")

    def test_rejects_empty_by_default(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            InputValidator.validate_string("", "name")

    def test_allows_empty_when_flag_set(self):
        result = InputValidator.validate_string("", "name", allow_empty=True)
        assert result == ""

    def test_rejects_whitespace_only(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            InputValidator.validate_string("   ", "name")

    def test_max_length_enforcement(self):
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            InputValidator.validate_string("a" * 256, "name", max_length=255)

    def test_max_length_boundary(self):
        result = InputValidator.validate_string("a" * 255, "name", max_length=255)
        assert len(result) == 255

    def test_min_length_enforcement(self):
        with pytest.raises(ValidationError, match="must be at least"):
            InputValidator.validate_string("ab", "name", min_length=3)

    def test_min_length_boundary(self):
        result = InputValidator.validate_string("abc", "name", min_length=3)
        assert result == "abc"

    def test_pattern_matching(self):
        alpha_pattern = re.compile(r"^[a-zA-Z]+$")
        result = InputValidator.validate_string("Hello", "name", pattern=alpha_pattern)
        assert result == "Hello"

    def test_pattern_rejection(self):
        alpha_pattern = re.compile(r"^[a-zA-Z]+$")
        with pytest.raises(ValidationError, match="does not match"):
            InputValidator.validate_string("Hello123", "name", pattern=alpha_pattern)

    def test_rejects_none(self):
        with pytest.raises(ValidationError, match="must be a string"):
            InputValidator.validate_string(None, "name")

    def test_rejects_list(self):
        with pytest.raises(ValidationError, match="must be a string"):
            InputValidator.validate_string(["a"], "name")


# ---------------------------------------------------------------------------
# validate_email
# ---------------------------------------------------------------------------

class TestValidateEmail:
    """Tests for InputValidator.validate_email"""

    def test_valid_email(self):
        result = InputValidator.validate_email("user@example.com")
        assert result == "user@example.com"

    def test_email_lowercased(self):
        result = InputValidator.validate_email("User@Example.COM")
        assert result == "user@example.com"

    def test_email_with_plus(self):
        result = InputValidator.validate_email("user+tag@example.com")
        assert result == "user+tag@example.com"

    def test_email_with_dots(self):
        result = InputValidator.validate_email("first.last@example.com")
        assert result == "first.last@example.com"

    def test_rejects_missing_at(self):
        with pytest.raises(ValidationError, match="not a valid email"):
            InputValidator.validate_email("userexample.com")

    def test_rejects_missing_domain(self):
        with pytest.raises(ValidationError, match="not a valid email"):
            InputValidator.validate_email("user@")

    def test_rejects_missing_tld(self):
        with pytest.raises(ValidationError, match="not a valid email"):
            InputValidator.validate_email("user@example")

    def test_rejects_empty(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_email("")

    def test_rejects_spaces(self):
        with pytest.raises(ValidationError, match="not a valid email"):
            InputValidator.validate_email("user @example.com")

    def test_max_length_254(self):
        long_local = "a" * 245
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            InputValidator.validate_email(f"{long_local}@example.com")


# ---------------------------------------------------------------------------
# sanitize_html
# ---------------------------------------------------------------------------

class TestSanitizeHtml:
    """Tests for InputValidator.sanitize_html"""

    def test_escapes_angle_brackets(self):
        result = InputValidator.sanitize_html("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result
        assert "&lt;" in result
        assert "&gt;" in result

    def test_escapes_quotes(self):
        result = InputValidator.sanitize_html('He said "hello"')
        assert "&quot;" in result

    def test_escapes_ampersand(self):
        result = InputValidator.sanitize_html("a & b")
        assert "&amp;" in result

    def test_plain_text_unchanged_semantically(self):
        text = "Hello World 123"
        result = InputValidator.sanitize_html(text)
        assert result == text

    def test_nested_tags(self):
        result = InputValidator.sanitize_html("<div><img src='x' onerror='alert(1)'></div>")
        assert "<div>" not in result
        assert "<img" not in result


# ---------------------------------------------------------------------------
# check_sql_injection
# ---------------------------------------------------------------------------

class TestCheckSqlInjection:
    """Tests for InputValidator.check_sql_injection"""

    def test_clean_input(self):
        # Should not raise
        InputValidator.check_sql_injection("normal search query", "search")

    def test_detects_select(self):
        with pytest.raises(ValidationError, match="SQL injection"):
            InputValidator.check_sql_injection("SELECT * FROM users", "query")

    def test_detects_drop(self):
        with pytest.raises(ValidationError, match="SQL injection"):
            InputValidator.check_sql_injection("DROP TABLE users", "query")

    def test_detects_union_select(self):
        with pytest.raises(ValidationError, match="SQL injection"):
            InputValidator.check_sql_injection("1 UNION SELECT password FROM users", "id")

    def test_case_insensitive(self):
        with pytest.raises(ValidationError, match="SQL injection"):
            InputValidator.check_sql_injection("select * from users", "query")

    def test_detects_insert(self):
        with pytest.raises(ValidationError, match="SQL injection"):
            InputValidator.check_sql_injection("INSERT INTO users VALUES('admin')", "query")

    def test_detects_delete(self):
        with pytest.raises(ValidationError, match="SQL injection"):
            InputValidator.check_sql_injection("DELETE FROM users WHERE id=1", "query")

    def test_detects_update(self):
        with pytest.raises(ValidationError, match="SQL injection"):
            InputValidator.check_sql_injection("UPDATE users SET admin=1", "query")
