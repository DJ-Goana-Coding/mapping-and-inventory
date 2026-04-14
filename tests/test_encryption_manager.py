"""
Tests for security/core/encryption_manager.py
Covers: key generation, encrypt/decrypt strings, encrypt/decrypt dicts,
        file encryption, password hashing, key rotation, SecretStore.
"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from security.core.encryption_manager import EncryptionManager, EncryptionError, SecretStore


# ---------------------------------------------------------------------------
# Key generation
# ---------------------------------------------------------------------------

class TestKeyGeneration:
    """Tests for key generation"""

    def test_generate_key_returns_bytes(self):
        key = EncryptionManager.generate_key()
        assert isinstance(key, bytes)

    def test_generate_key_is_unique(self):
        key1 = EncryptionManager.generate_key()
        key2 = EncryptionManager.generate_key()
        assert key1 != key2

    def test_init_with_no_key_generates_one(self):
        manager = EncryptionManager()
        assert manager.master_key is not None
        assert isinstance(manager.master_key, bytes)

    def test_init_with_explicit_key(self):
        key = EncryptionManager.generate_key()
        manager = EncryptionManager(master_key=key)
        assert manager.master_key == key


# ---------------------------------------------------------------------------
# String encryption/decryption
# ---------------------------------------------------------------------------

class TestStringEncryption:
    """Tests for encrypt/decrypt string operations"""

    def setup_method(self):
        self.manager = EncryptionManager()

    def test_encrypt_decrypt_roundtrip(self):
        plaintext = "my-secret-api-key-12345"
        encrypted = self.manager.encrypt(plaintext)
        decrypted = self.manager.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypted_differs_from_plaintext(self):
        plaintext = "my-secret"
        encrypted = self.manager.encrypt(plaintext)
        assert encrypted != plaintext

    def test_encrypt_empty_string(self):
        encrypted = self.manager.encrypt("")
        decrypted = self.manager.decrypt(encrypted)
        assert decrypted == ""

    def test_encrypt_unicode(self):
        plaintext = "日本語テスト 🔒"
        encrypted = self.manager.encrypt(plaintext)
        decrypted = self.manager.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_long_string(self):
        plaintext = "x" * 10000
        encrypted = self.manager.encrypt(plaintext)
        decrypted = self.manager.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_rejects_non_string(self):
        with pytest.raises(EncryptionError, match="must be a string"):
            self.manager.encrypt(12345)

    def test_decrypt_with_wrong_key_fails(self):
        encrypted = self.manager.encrypt("secret")
        other_manager = EncryptionManager()  # Different key
        with pytest.raises(EncryptionError, match="Decryption failed"):
            other_manager.decrypt(encrypted)

    def test_decrypt_corrupted_data_fails(self):
        with pytest.raises(EncryptionError, match="Decryption failed"):
            self.manager.decrypt("not-valid-ciphertext-at-all")


# ---------------------------------------------------------------------------
# Dictionary encryption/decryption
# ---------------------------------------------------------------------------

class TestDictEncryption:
    """Tests for encrypt_dict/decrypt_dict"""

    def setup_method(self):
        self.manager = EncryptionManager()

    def test_dict_roundtrip(self):
        data = {"api_key": "sk-123", "secret": "abc"}
        encrypted = self.manager.encrypt_dict(data)
        decrypted = self.manager.decrypt_dict(encrypted)
        assert decrypted == data

    def test_nested_dict(self):
        data = {"outer": {"inner": {"deep": "value"}}}
        encrypted = self.manager.encrypt_dict(data)
        decrypted = self.manager.decrypt_dict(encrypted)
        assert decrypted == data

    def test_dict_with_list(self):
        data = {"items": [1, 2, 3], "name": "test"}
        encrypted = self.manager.encrypt_dict(data)
        decrypted = self.manager.decrypt_dict(encrypted)
        assert decrypted == data

    def test_empty_dict(self):
        data = {}
        encrypted = self.manager.encrypt_dict(data)
        decrypted = self.manager.decrypt_dict(encrypted)
        assert decrypted == data


# ---------------------------------------------------------------------------
# File encryption
# ---------------------------------------------------------------------------

class TestFileEncryption:
    """Tests for encrypt_file/decrypt_file"""

    def setup_method(self):
        self.manager = EncryptionManager()

    def test_file_roundtrip(self, tmp_path):
        # Create a plaintext file
        original = tmp_path / "secret.txt"
        original.write_text("This is secret content")

        # Encrypt
        encrypted_path = self.manager.encrypt_file(original)
        assert encrypted_path.exists()
        assert encrypted_path.suffix == ".enc"

        # Decrypt
        decrypted_path = self.manager.decrypt_file(encrypted_path)
        assert decrypted_path.exists()
        assert decrypted_path.read_text() == "This is secret content"

    def test_encrypt_file_custom_output(self, tmp_path):
        original = tmp_path / "data.json"
        original.write_text('{"key": "value"}')

        output = tmp_path / "encrypted_data.bin"
        result = self.manager.encrypt_file(original, output)
        assert result == output
        assert output.exists()

    def test_encrypt_nonexistent_file(self, tmp_path):
        with pytest.raises(EncryptionError, match="not found"):
            self.manager.encrypt_file(tmp_path / "nonexistent.txt")

    def test_decrypt_nonexistent_file(self, tmp_path):
        with pytest.raises(EncryptionError, match="not found"):
            self.manager.decrypt_file(tmp_path / "nonexistent.enc")


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    """Tests for hash_password/verify_password"""

    def test_hash_password(self):
        key, salt = EncryptionManager.hash_password("mypassword")
        assert isinstance(key, bytes)
        assert isinstance(salt, bytes)
        assert len(salt) == 32

    def test_verify_correct_password(self):
        key, salt = EncryptionManager.hash_password("mypassword")
        assert EncryptionManager.verify_password("mypassword", key, salt) is True

    def test_verify_wrong_password(self):
        key, salt = EncryptionManager.hash_password("mypassword")
        assert EncryptionManager.verify_password("wrongpassword", key, salt) is False

    def test_deterministic_with_same_salt(self):
        salt = b"0" * 32
        key1, _ = EncryptionManager.hash_password("test", salt)
        key2, _ = EncryptionManager.hash_password("test", salt)
        assert key1 == key2

    def test_different_salt_different_hash(self):
        key1, salt1 = EncryptionManager.hash_password("test")
        key2, salt2 = EncryptionManager.hash_password("test")
        # Salts should differ (random)
        assert salt1 != salt2
        assert key1 != key2


# ---------------------------------------------------------------------------
# Key rotation
# ---------------------------------------------------------------------------

class TestKeyRotation:
    """Tests for rotate_key"""

    def test_rotate_key_changes_cipher(self):
        manager = EncryptionManager()
        old_key = manager.master_key
        new_key = manager.rotate_key()
        assert new_key != old_key
        assert manager.master_key == new_key

    def test_rotate_with_explicit_key(self):
        manager = EncryptionManager()
        new_key = EncryptionManager.generate_key()
        returned = manager.rotate_key(new_key)
        assert returned == new_key
        assert manager.master_key == new_key

    def test_old_ciphertext_fails_after_rotation(self):
        manager = EncryptionManager()
        encrypted = manager.encrypt("secret")
        manager.rotate_key()
        with pytest.raises(EncryptionError):
            manager.decrypt(encrypted)


# ---------------------------------------------------------------------------
# SecretStore
# ---------------------------------------------------------------------------

class TestSecretStore:
    """Tests for SecretStore"""

    def setup_method(self):
        self.manager = EncryptionManager()

    def test_set_and_get(self, tmp_path):
        store = SecretStore(tmp_path / "secrets.enc", self.manager)
        store.set("api_key", "sk-12345")
        assert store.get("api_key") == "sk-12345"

    def test_get_missing_returns_default(self, tmp_path):
        store = SecretStore(tmp_path / "secrets.enc", self.manager)
        assert store.get("missing") is None
        assert store.get("missing", "fallback") == "fallback"

    def test_delete(self, tmp_path):
        store = SecretStore(tmp_path / "secrets.enc", self.manager)
        store.set("temp_key", "value")
        store.delete("temp_key")
        assert store.get("temp_key") is None

    def test_list_keys(self, tmp_path):
        store = SecretStore(tmp_path / "secrets.enc", self.manager)
        store.set("key1", "v1")
        store.set("key2", "v2")
        keys = store.list_keys()
        assert "key1" in keys
        assert "key2" in keys

    def test_save_and_load(self, tmp_path):
        store_path = tmp_path / "secrets.enc"
        store = SecretStore(store_path, self.manager)
        store.set("api_key", "sk-persist")
        store.save()

        # Load in a new store instance
        store2 = SecretStore(store_path, self.manager)
        assert store2.get("api_key") == "sk-persist"

    def test_save_creates_file(self, tmp_path):
        store_path = tmp_path / "sub" / "secrets.enc"
        store = SecretStore(store_path, self.manager)
        store.set("key", "value")
        store.save()
        assert store_path.exists()

    def test_overwrite_key(self, tmp_path):
        store = SecretStore(tmp_path / "secrets.enc", self.manager)
        store.set("key", "old")
        store.set("key", "new")
        assert store.get("key") == "new"

    def test_save_key_to_file(self, tmp_path):
        key_path = tmp_path / "master.key"
        self.manager.save_key(key_path)
        assert key_path.exists()
        assert key_path.read_bytes().strip() == self.manager.master_key
