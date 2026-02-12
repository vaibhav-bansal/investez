"""
Encryption utilities for sensitive data.
Uses Fernet (symmetric encryption) from cryptography library.
"""

import os
from cryptography.fernet import Fernet


def get_encryption_key() -> bytes:
    """
    Get or generate encryption key from environment variable.
    The key should be a 32-byte base64-encoded string.
    """
    key_str = os.getenv("DB_ENCRYPTION_KEY")

    if not key_str:
        raise ValueError(
            "DB_ENCRYPTION_KEY not set in environment. "
            "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )

    try:
        # Validate it's a valid Fernet key
        key = key_str.encode()
        Fernet(key)  # This will raise if invalid
        return key
    except Exception as e:
        raise ValueError(f"Invalid DB_ENCRYPTION_KEY: {e}")


def encrypt_data(plaintext: str) -> str:
    """
    Encrypt plaintext string and return base64-encoded ciphertext.

    Args:
        plaintext: String to encrypt

    Returns:
        Base64-encoded encrypted string
    """
    if not plaintext:
        return ""

    key = get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(plaintext.encode())
    return encrypted.decode()


def decrypt_data(ciphertext: str) -> str:
    """
    Decrypt base64-encoded ciphertext and return plaintext string.

    Args:
        ciphertext: Base64-encoded encrypted string

    Returns:
        Decrypted plaintext string
    """
    if not ciphertext:
        return ""

    key = get_encryption_key()
    f = Fernet(key)
    decrypted = f.decrypt(ciphertext.encode())
    return decrypted.decode()


def generate_key() -> str:
    """
    Generate a new Fernet encryption key.
    Use this to generate DB_ENCRYPTION_KEY for .env file.

    Returns:
        Base64-encoded encryption key as string
    """
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    # Generate a new key when run directly
    print("Generated encryption key:")
    print(generate_key())
    print("\nAdd this to your .env file as DB_ENCRYPTION_KEY")
