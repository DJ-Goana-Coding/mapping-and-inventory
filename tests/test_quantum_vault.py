"""
Tests for security/core/quantum_vault.py
Covers: vault init, credential CRUD, list/filter, save/load, metadata,
        EmailCredentialManager, GDriveCredentialManager, audit log.
"""

import os
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from security.core.quantum_vault import (
    QuantumVault,
    QuantumVaultError,
    CredentialMetadata,
    EmailCredentialManager,
    GDriveCredentialManager,
)


@pytest.fixture
def master_key():
    """Generate a fresh master key for tests."""
    return QuantumVault.generate_master_key()


@pytest.fixture
def vault(tmp_path, master_key):
    """Create a fresh QuantumVault instance."""
    vault_path = tmp_path / "test_vault.enc"
    return QuantumVault(vault_path, master_key=master_key)


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestVaultInit:
    """Tests for QuantumVault initialization"""

    def test_create_vault_with_master_key(self, tmp_path, master_key):
        v = QuantumVault(tmp_path / "v.enc", master_key=master_key)
        assert v.vault_path == tmp_path / "v.enc"

    def test_generate_master_key(self):
        key = QuantumVault.generate_master_key()
        assert isinstance(key, str)
        assert len(key) > 0

    def test_generate_master_key_unique(self):
        k1 = QuantumVault.generate_master_key()
        k2 = QuantumVault.generate_master_key()
        assert k1 != k2

    def test_vault_requires_key(self, tmp_path):
        # Ensure env var is not set
        os.environ.pop('QUANTUM_VAULT_KEY', None)
        with pytest.raises(QuantumVaultError, match="Master key required"):
            QuantumVault(tmp_path / "v.enc", use_env_key=True)

    def test_vault_from_env_var(self, tmp_path, master_key):
        os.environ['QUANTUM_VAULT_KEY'] = master_key
        try:
            v = QuantumVault(tmp_path / "v.enc")
            assert v is not None
        finally:
            del os.environ['QUANTUM_VAULT_KEY']

    def test_creates_parent_directory(self, tmp_path, master_key):
        deep_path = tmp_path / "sub" / "dir" / "vault.enc"
        v = QuantumVault(deep_path, master_key=master_key)
        assert deep_path.parent.exists()


# ---------------------------------------------------------------------------
# Credential CRUD
# ---------------------------------------------------------------------------

class TestCredentialCRUD:
    """Tests for store, retrieve, delete credentials"""

    def test_store_and_retrieve(self, vault):
        vault.store_credential("cred1", {"user": "admin", "pass": "secret"})
        result = vault.retrieve_credential("cred1")
        assert result == {"user": "admin", "pass": "secret"}

    def test_retrieve_nonexistent(self, vault):
        result = vault.retrieve_credential("does_not_exist")
        assert result is None

    def test_delete_existing(self, vault):
        vault.store_credential("temp", {"value": "x"})
        assert vault.delete_credential("temp") is True
        assert vault.retrieve_credential("temp") is None

    def test_delete_nonexistent(self, vault):
        assert vault.delete_credential("missing") is False

    def test_overwrite_credential(self, vault):
        vault.store_credential("cred", {"v": 1})
        vault.store_credential("cred", {"v": 2})
        result = vault.retrieve_credential("cred")
        assert result == {"v": 2}

    def test_store_with_tags(self, vault):
        vault.store_credential("tagged", {"x": 1}, tags=["email", "gmail"])
        meta = vault.get_metadata("tagged")
        assert "email" in meta.tags
        assert "gmail" in meta.tags


# ---------------------------------------------------------------------------
# List and filter
# ---------------------------------------------------------------------------

class TestListCredentials:
    """Tests for list_credentials with optional tag filter"""

    def test_list_all(self, vault):
        vault.store_credential("a", {"v": 1})
        vault.store_credential("b", {"v": 2})
        result = vault.list_credentials()
        assert "a" in result
        assert "b" in result

    def test_list_empty(self, vault):
        assert vault.list_credentials() == []

    def test_filter_by_tag(self, vault):
        vault.store_credential("email1", {"v": 1}, tags=["email"])
        vault.store_credential("api1", {"v": 2}, tags=["api"])
        vault.store_credential("email2", {"v": 3}, tags=["email"])

        email_creds = vault.list_credentials(tag="email")
        assert len(email_creds) == 2
        assert "api1" not in email_creds

    def test_filter_no_match(self, vault):
        vault.store_credential("a", {"v": 1}, tags=["x"])
        result = vault.list_credentials(tag="nonexistent")
        assert result == []


# ---------------------------------------------------------------------------
# Metadata and access tracking
# ---------------------------------------------------------------------------

class TestMetadata:
    """Tests for credential metadata tracking"""

    def test_metadata_created(self, vault):
        vault.store_credential("m1", {"v": 1})
        meta = vault.get_metadata("m1")
        assert meta is not None
        assert meta.created_at is not None
        assert meta.access_count == 0

    def test_access_count_increments(self, vault):
        vault.store_credential("m2", {"v": 1})
        vault.retrieve_credential("m2")
        vault.retrieve_credential("m2")
        meta = vault.get_metadata("m2")
        assert meta.access_count == 2

    def test_last_accessed_updated(self, vault):
        vault.store_credential("m3", {"v": 1})
        assert vault.get_metadata("m3").last_accessed is None
        vault.retrieve_credential("m3")
        assert vault.get_metadata("m3").last_accessed is not None

    def test_metadata_nonexistent(self, vault):
        assert vault.get_metadata("missing") is None


# ---------------------------------------------------------------------------
# Save and load
# ---------------------------------------------------------------------------

class TestSaveLoad:
    """Tests for vault persistence"""

    def test_save_and_load(self, tmp_path, master_key):
        vault_path = tmp_path / "persist.enc"
        v1 = QuantumVault(vault_path, master_key=master_key)
        v1.store_credential("persist_cred", {"key": "value123"}, tags=["test"])
        v1.save()

        # Load in new instance
        v2 = QuantumVault(vault_path, master_key=master_key)
        result = v2.retrieve_credential("persist_cred")
        assert result == {"key": "value123"}

    def test_load_preserves_metadata(self, tmp_path, master_key):
        vault_path = tmp_path / "meta.enc"
        v1 = QuantumVault(vault_path, master_key=master_key)
        v1.store_credential("meta_cred", {"x": 1}, tags=["tag1"])
        v1.retrieve_credential("meta_cred")  # access_count = 1
        v1.save()

        v2 = QuantumVault(vault_path, master_key=master_key)
        meta = v2.get_metadata("meta_cred")
        assert meta.access_count == 1
        assert "tag1" in meta.tags

    def test_wrong_key_fails_load(self, tmp_path, master_key):
        vault_path = tmp_path / "wrong_key.enc"
        v1 = QuantumVault(vault_path, master_key=master_key)
        v1.store_credential("secret", {"data": "x"})
        v1.save()

        wrong_key = QuantumVault.generate_master_key()
        with pytest.raises(QuantumVaultError, match="Failed to load"):
            QuantumVault(vault_path, master_key=wrong_key)

    def test_save_creates_file(self, vault):
        vault.store_credential("c", {"v": 1})
        vault.save()
        assert vault.vault_path.exists()


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

class TestAuditLog:
    """Tests for audit_log method"""

    def test_audit_log_structure(self, vault):
        vault.store_credential("a1", {"v": 1}, tags=["t1"])
        vault.retrieve_credential("a1")
        audit = vault.audit_log()

        assert audit['total_credentials'] == 1
        assert len(audit['credentials']) == 1
        assert audit['credentials'][0]['id'] == 'a1'
        assert audit['credentials'][0]['access_count'] == 1
        assert 'audit_timestamp' in audit

    def test_audit_log_empty(self, vault):
        audit = vault.audit_log()
        assert audit['total_credentials'] == 0
        assert audit['credentials'] == []


# ---------------------------------------------------------------------------
# EmailCredentialManager
# ---------------------------------------------------------------------------

class TestEmailCredentialManager:
    """Tests for EmailCredentialManager"""

    def test_add_and_get_email(self, vault):
        mgr = EmailCredentialManager(vault)
        mgr.add_email_account("user@gmail.com", "pass123", provider="gmail")
        cred = mgr.get_email_account("user@gmail.com")
        assert cred is not None
        assert cred['email'] == "user@gmail.com"
        assert cred['password'] == "pass123"
        assert cred['provider'] == "gmail"
        assert cred['imap_server'] == "imap.gmail.com"

    def test_gmail_defaults(self, vault):
        mgr = EmailCredentialManager(vault)
        mgr.add_email_account("u@gmail.com", "p", provider="gmail")
        cred = mgr.get_email_account("u@gmail.com")
        assert cred['smtp_server'] == "smtp.gmail.com"
        assert cred['imap_port'] == 993
        assert cred['smtp_port'] == 587

    def test_yahoo_defaults(self, vault):
        mgr = EmailCredentialManager(vault)
        mgr.add_email_account("u@yahoo.com", "p", provider="yahoo")
        cred = mgr.get_email_account("u@yahoo.com")
        assert cred['imap_server'] == "imap.mail.yahoo.com"

    def test_outlook_defaults(self, vault):
        mgr = EmailCredentialManager(vault)
        mgr.add_email_account("u@outlook.com", "p", provider="outlook")
        cred = mgr.get_email_account("u@outlook.com")
        assert cred['imap_server'] == "outlook.office365.com"

    def test_list_email_accounts(self, vault):
        mgr = EmailCredentialManager(vault)
        mgr.add_email_account("a@gmail.com", "p1")
        mgr.add_email_account("b@gmail.com", "p2")
        emails = mgr.list_email_accounts()
        assert "a@gmail.com" in emails
        assert "b@gmail.com" in emails

    def test_get_nonexistent_email(self, vault):
        mgr = EmailCredentialManager(vault)
        assert mgr.get_email_account("missing@test.com") is None


# ---------------------------------------------------------------------------
# GDriveCredentialManager
# ---------------------------------------------------------------------------

class TestGDriveCredentialManager:
    """Tests for GDriveCredentialManager"""

    def test_add_and_get_gdrive(self, vault):
        mgr = GDriveCredentialManager(vault)
        mgr.add_gdrive_account("user@gmail.com", "gpass")
        cred = mgr.get_gdrive_account("user@gmail.com")
        assert cred is not None
        assert cred['email'] == "user@gmail.com"
        assert cred['type'] == "gdrive"
        assert len(cred['scopes']) == 3

    def test_list_gdrive_accounts(self, vault):
        mgr = GDriveCredentialManager(vault)
        mgr.add_gdrive_account("a@gmail.com", "p")
        mgr.add_gdrive_account("b@gmail.com", "p")
        accounts = mgr.list_gdrive_accounts()
        assert "a@gmail.com" in accounts
        assert "b@gmail.com" in accounts

    def test_get_nonexistent_gdrive(self, vault):
        mgr = GDriveCredentialManager(vault)
        assert mgr.get_gdrive_account("missing@test.com") is None


# ---------------------------------------------------------------------------
# CredentialMetadata dataclass
# ---------------------------------------------------------------------------

class TestCredentialMetadata:
    """Tests for CredentialMetadata"""

    def test_default_tags(self):
        meta = CredentialMetadata(created_at="2025-01-01", updated_at="2025-01-01")
        assert meta.tags == []

    def test_access_count_default(self):
        meta = CredentialMetadata(created_at="2025-01-01", updated_at="2025-01-01")
        assert meta.access_count == 0
        assert meta.last_accessed is None
