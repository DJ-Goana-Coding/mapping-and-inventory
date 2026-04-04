"""
🔒 ENCRYPTION MANAGER - Secrets Encryption & Key Management
Encrypts: API keys, credentials, sensitive data at rest
"""

import os
import json
import base64
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class EncryptionError(Exception):
    """Encryption operation error"""
    pass


class EncryptionManager:
    """
    Manage encryption of secrets and sensitive data
    Uses AES-256-GCM via cryptography library (Fernet)
    """
    
    def __init__(self, master_key: Optional[bytes] = None, key_file: Optional[Path] = None):
        """
        Initialize encryption manager
        
        Args:
            master_key: Master encryption key (32 bytes)
            key_file: Path to file containing master key
        """
        try:
            from cryptography.fernet import Fernet
            self.Fernet = Fernet
        except ImportError:
            raise ImportError("cryptography library required: pip install cryptography")
        
        # Load or generate master key
        if master_key:
            self.master_key = master_key
        elif key_file and Path(key_file).exists():
            self.master_key = Path(key_file).read_bytes().strip()
        else:
            # Generate new key
            self.master_key = Fernet.generate_key()
            print("⚠️ Generated new master key. Save it securely!")
        
        self.cipher = Fernet(self.master_key)
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new Fernet encryption key"""
        from cryptography.fernet import Fernet
        return Fernet.generate_key()
    
    def save_key(self, filepath: Path, permissions: int = 0o600) -> None:
        """
        Save master key to file with restricted permissions
        
        Args:
            filepath: Path to save key
            permissions: Unix file permissions (default: 0o600 = owner read/write only)
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_bytes(self.master_key)
        
        # Set restrictive permissions (Unix only)
        try:
            os.chmod(filepath, permissions)
            print(f"✅ Key saved to {filepath} with permissions {oct(permissions)}")
        except Exception as e:
            print(f"⚠️ Could not set permissions: {e}")
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            Base64-encoded ciphertext
        """
        if not isinstance(plaintext, str):
            raise EncryptionError("Plaintext must be a string")
        
        ciphertext = self.cipher.encrypt(plaintext.encode('utf-8'))
        return base64.b64encode(ciphertext).decode('ascii')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string
        
        Args:
            ciphertext: Base64-encoded ciphertext
        
        Returns:
            Decrypted plaintext string
        """
        try:
            ciphertext_bytes = base64.b64decode(ciphertext.encode('ascii'))
            plaintext = self.cipher.decrypt(ciphertext_bytes)
            return plaintext.decode('utf-8')
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {e}")
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """
        Encrypt dictionary as JSON
        
        Args:
            data: Dictionary to encrypt
        
        Returns:
            Encrypted JSON string
        """
        json_str = json.dumps(data)
        return self.encrypt(json_str)
    
    def decrypt_dict(self, ciphertext: str) -> Dict[str, Any]:
        """
        Decrypt JSON dictionary
        
        Args:
            ciphertext: Encrypted JSON string
        
        Returns:
            Decrypted dictionary
        """
        json_str = self.decrypt(ciphertext)
        return json.loads(json_str)
    
    def encrypt_file(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Encrypt entire file
        
        Args:
            input_path: Path to file to encrypt
            output_path: Path for encrypted output (default: input_path + '.enc')
        
        Returns:
            Path to encrypted file
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise EncryptionError(f"Input file not found: {input_path}")
        
        if output_path is None:
            output_path = Path(str(input_path) + '.enc')
        else:
            output_path = Path(output_path)
        
        # Read and encrypt
        plaintext = input_path.read_bytes()
        ciphertext = self.cipher.encrypt(plaintext)
        
        # Write encrypted file
        output_path.write_bytes(ciphertext)
        print(f"✅ Encrypted {input_path} -> {output_path}")
        
        return output_path
    
    def decrypt_file(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Decrypt entire file
        
        Args:
            input_path: Path to encrypted file
            output_path: Path for decrypted output
        
        Returns:
            Path to decrypted file
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise EncryptionError(f"Input file not found: {input_path}")
        
        if output_path is None:
            # Remove .enc extension if present
            if input_path.suffix == '.enc':
                output_path = input_path.with_suffix('')
            else:
                output_path = Path(str(input_path) + '.dec')
        else:
            output_path = Path(output_path)
        
        # Read and decrypt
        ciphertext = input_path.read_bytes()
        plaintext = self.cipher.decrypt(ciphertext)
        
        # Write decrypted file
        output_path.write_bytes(plaintext)
        print(f"✅ Decrypted {input_path} -> {output_path}")
        
        return output_path
    
    def encrypt_env_file(self, env_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Encrypt .env file
        
        Args:
            env_path: Path to .env file
            output_path: Path for encrypted output
        
        Returns:
            Path to encrypted file
        """
        env_path = Path(env_path)
        if output_path is None:
            output_path = env_path.parent / (env_path.name + '.enc')
        
        return self.encrypt_file(env_path, output_path)
    
    def decrypt_env_file(self, encrypted_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Decrypt .env file
        
        Args:
            encrypted_path: Path to encrypted .env file
            output_path: Path for decrypted output
        
        Returns:
            Path to decrypted file
        """
        return self.decrypt_file(encrypted_path, output_path)
    
    def rotate_key(self, new_key: Optional[bytes] = None) -> bytes:
        """
        Rotate encryption key
        
        Args:
            new_key: New master key (generates one if not provided)
        
        Returns:
            New master key
        """
        if new_key is None:
            new_key = self.generate_key()
        
        old_cipher = self.cipher
        self.master_key = new_key
        self.cipher = self.Fernet(new_key)
        
        print("✅ Encryption key rotated. Re-encrypt all secrets with new key!")
        return new_key
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Hash password using PBKDF2
        
        Args:
            password: Password to hash
            salt: Salt bytes (generates if not provided)
        
        Returns:
            (hash, salt) tuple
        """
        if salt is None:
            salt = os.urandom(32)
        
        # PBKDF2 with 100,000 iterations
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        
        return key, salt
    
    @staticmethod
    def verify_password(password: str, key: bytes, salt: bytes) -> bool:
        """Verify password against hash"""
        new_key, _ = EncryptionManager.hash_password(password, salt)
        return new_key == key


class SecretStore:
    """Encrypted secret storage"""
    
    def __init__(self, store_path: Path, encryption_manager: EncryptionManager):
        """
        Initialize secret store
        
        Args:
            store_path: Path to encrypted secrets file
            encryption_manager: EncryptionManager instance
        """
        self.store_path = Path(store_path)
        self.encryption_manager = encryption_manager
        self._secrets: Dict[str, Any] = {}
        
        # Load existing secrets
        if self.store_path.exists():
            self.load()
    
    def set(self, key: str, value: Any) -> None:
        """Store a secret"""
        self._secrets[key] = {
            'value': value,
            'updated_at': datetime.utcnow().isoformat()
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a secret"""
        secret = self._secrets.get(key)
        return secret['value'] if secret else default
    
    def delete(self, key: str) -> None:
        """Delete a secret"""
        if key in self._secrets:
            del self._secrets[key]
    
    def list_keys(self) -> list:
        """List all secret keys"""
        return list(self._secrets.keys())
    
    def save(self) -> None:
        """Save secrets to encrypted file"""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        encrypted_data = self.encryption_manager.encrypt_dict(self._secrets)
        self.store_path.write_text(encrypted_data)
        print(f"✅ Secrets saved to {self.store_path}")
    
    def load(self) -> None:
        """Load secrets from encrypted file"""
        if not self.store_path.exists():
            return
        
        encrypted_data = self.store_path.read_text()
        self._secrets = self.encryption_manager.decrypt_dict(encrypted_data)
        print(f"✅ Secrets loaded from {self.store_path}")


if __name__ == "__main__":
    print("🔒 Encryption Manager Test\n")
    
    # Generate key
    manager = EncryptionManager()
    print(f"Master key (save securely): {manager.master_key.decode('ascii')}\n")
    
    # Encrypt/decrypt string
    secret = "my-api-key-12345"
    encrypted = manager.encrypt(secret)
    print(f"Encrypted: {encrypted}")
    
    decrypted = manager.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    print(f"Match: {secret == decrypted}\n")
    
    # Encrypt/decrypt dict
    credentials = {
        'api_key': 'sk-1234567890',
        'api_secret': 'secret-abcdef',
        'endpoint': 'https://api.example.com'
    }
    
    encrypted_creds = manager.encrypt_dict(credentials)
    print(f"Encrypted credentials: {encrypted_creds[:50]}...")
    
    decrypted_creds = manager.decrypt_dict(encrypted_creds)
    print(f"Decrypted: {decrypted_creds}\n")
    
    # Secret store
    store = SecretStore(Path("/tmp/secrets.enc"), manager)
    store.set('mexc_api_key', 'mx0-key-123')
    store.set('mexc_api_secret', 'mx0-secret-456')
    store.save()
    
    print(f"Stored secrets: {store.list_keys()}")
