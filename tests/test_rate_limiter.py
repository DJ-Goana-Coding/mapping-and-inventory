"""
Tests for security/core/rate_limiter.py
Covers: rate parsing, memory-based limiting, rate exceeded, reset, stats, decorator.
"""

import time
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from security.core.rate_limiter import RateLimiter, RateLimitExceeded, rate_limit


# ---------------------------------------------------------------------------
# _parse_rate
# ---------------------------------------------------------------------------

class TestParseRate:
    """Tests for RateLimiter._parse_rate"""

    def setup_method(self):
        self.limiter = RateLimiter(storage_backend='memory')

    def test_parse_per_second(self):
        limit, period = self.limiter._parse_rate("10/second")
        assert limit == 10
        assert period == 1

    def test_parse_per_minute(self):
        limit, period = self.limiter._parse_rate("100/minute")
        assert limit == 100
        assert period == 60

    def test_parse_per_hour(self):
        limit, period = self.limiter._parse_rate("1000/hour")
        assert limit == 1000
        assert period == 3600

    def test_parse_per_day(self):
        limit, period = self.limiter._parse_rate("5000/day")
        assert limit == 5000
        assert period == 86400

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid rate format"):
            self.limiter._parse_rate("100")

    def test_invalid_period(self):
        with pytest.raises(ValueError, match="Invalid period"):
            self.limiter._parse_rate("100/week")


# ---------------------------------------------------------------------------
# Memory-based rate limiting
# ---------------------------------------------------------------------------

class TestMemoryRateLimiting:
    """Tests for in-memory rate limiting"""

    def setup_method(self):
        self.limiter = RateLimiter(storage_backend='memory')

    def test_allows_within_limit(self):
        info = self.limiter.check_rate_limit("user1", "5/second", "test")
        assert info['allowed'] is True
        assert info['limit'] == 5

    def test_tracks_remaining(self):
        info = self.limiter.check_rate_limit("user2", "5/second", "test")
        assert info['remaining'] == 4

        info = self.limiter.check_rate_limit("user2", "5/second", "test")
        assert info['remaining'] == 3

    def test_exceeds_limit(self):
        for i in range(3):
            self.limiter.check_rate_limit("user3", "3/second", "test")

        with pytest.raises(RateLimitExceeded, match="Rate limit exceeded"):
            self.limiter.check_rate_limit("user3", "3/second", "test")

    def test_different_identifiers_independent(self):
        for i in range(3):
            self.limiter.check_rate_limit("userA", "3/second", "test")

        # Different identifier should still work
        info = self.limiter.check_rate_limit("userB", "3/second", "test")
        assert info['allowed'] is True

    def test_different_namespaces_independent(self):
        for i in range(3):
            self.limiter.check_rate_limit("user4", "3/second", "ns1")

        # Same user, different namespace should still work
        info = self.limiter.check_rate_limit("user4", "3/second", "ns2")
        assert info['allowed'] is True

    def test_info_has_reset_at(self):
        info = self.limiter.check_rate_limit("user5", "10/minute", "test")
        assert 'reset_at' in info
        assert 'retry_after' in info


# ---------------------------------------------------------------------------
# Convenience methods
# ---------------------------------------------------------------------------

class TestConvenienceMethods:
    """Tests for limit_by_ip, limit_by_user, limit_by_api_key"""

    def setup_method(self):
        self.limiter = RateLimiter(storage_backend='memory')

    def test_limit_by_ip(self):
        info = self.limiter.limit_by_ip("192.168.1.1", "10/second")
        assert info['allowed'] is True

    def test_limit_by_user(self):
        info = self.limiter.limit_by_user("user123", "10/second")
        assert info['allowed'] is True

    def test_limit_by_api_key(self):
        info = self.limiter.limit_by_api_key("sk-12345", "10/second")
        assert info['allowed'] is True


# ---------------------------------------------------------------------------
# Reset and Stats
# ---------------------------------------------------------------------------

class TestResetAndStats:
    """Tests for reset and get_stats"""

    def setup_method(self):
        self.limiter = RateLimiter(storage_backend='memory')

    def test_reset_clears_limit(self):
        # Fill up the limit
        for i in range(3):
            self.limiter.check_rate_limit("user6", "3/second", "test")

        # Should be at limit
        with pytest.raises(RateLimitExceeded):
            self.limiter.check_rate_limit("user6", "3/second", "test")

        # Reset
        self.limiter.reset("user6", "test")

        # Should work again
        info = self.limiter.check_rate_limit("user6", "3/second", "test")
        assert info['allowed'] is True

    def test_stats_empty(self):
        stats = self.limiter.get_stats("newuser", "test")
        assert stats['current_count'] == 0
        assert stats['identifier'] == "newuser"
        assert stats['namespace'] == "test"
        assert stats['storage_backend'] == 'memory'

    def test_stats_after_requests(self):
        self.limiter.check_rate_limit("user7", "10/second", "test")
        self.limiter.check_rate_limit("user7", "10/second", "test")

        stats = self.limiter.get_stats("user7", "test")
        assert stats['current_count'] == 2


# ---------------------------------------------------------------------------
# rate_limit decorator
# ---------------------------------------------------------------------------

class TestRateLimitDecorator:
    """Tests for the @rate_limit decorator"""

    def test_decorated_function_executes(self):
        @rate_limit("100/second", namespace="test_deco")
        def my_func(x):
            return x * 2

        result = my_func("hello")
        assert result == "hellohello"

    def test_decorated_function_rate_limited(self):
        @rate_limit("2/second", namespace="test_deco_limit")
        def limited_func(x):
            return x

        limited_func("a")
        limited_func("a")

        with pytest.raises(RateLimitExceeded):
            limited_func("a")
