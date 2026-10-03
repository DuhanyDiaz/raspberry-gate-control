"""
Módulo de Criptografía Simétrica para Protección de PINs (Fase 3)
Proyecto: Control de Accesos FIUSAC / EMI

Utiliza Fernet (AES-128-CBC + HMAC-SHA256) para garantizar confidencialidad
e integridad de los PINs almacenados en la base de datos, permitiendo su
descifrado para el usuario y admin autenticados.
"""

import os
from cryptography.fernet import Fernet, InvalidToken

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(BASE_DIR, ".pin_key")

def _obtener_clave_fernet() -> bytes:
    # 1. Si existe en variable de entorno
    env_key = os.getenv("PIN_ENCRYPTION_KEY")
    if env_key:
        return env_key.strip().encode()

    # 2. Si existe en el archivo local persistente
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read().strip()

    # 3. Si no existe, generar una nueva y persistirla en disco
    nueva_clave = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(nueva_clave)
    # Permisos restrictivos (solo lectura/escritura por el propietario)
    try:
        os.chmod(KEY_FILE, 0o600)
    except Exception:
        pass
    return nueva_clave

_fernet_instance = Fernet(_obtener_clave_fernet())

def encrypt_pin(plain_pin: str) -> str:
    """Cifra un PIN de 4 dígitos para almacenarlo de forma segura en la base de datos."""
    if not plain_pin:
        return plain_pin
    token = _fernet_instance.encrypt(str(plain_pin).encode("utf-8"))
    return token.decode("utf-8")

def decrypt_pin(cipher_pin: str) -> str:
    """
    Descifra un PIN almacenado.
    Es tolerante a fallos: si el valor ya era texto plano o no es un token Fernet,
    devuelve el valor original para no romper nunca la operación del sistema.
    """
    if not cipher_pin:
        return cipher_pin
    try:
        plain_bytes = _fernet_instance.decrypt(cipher_pin.encode("utf-8"))
        return plain_bytes.decode("utf-8")
    except (InvalidToken, Exception):
        # Fallback seguro: si era un PIN antiguo sin cifrar, devolverlo directamente
        return cipher_pin

def is_encrypted(val: str) -> bool:
    """Verifica si una cadena ya está cifrada con Fernet."""
    if not val or len(val) < 50:
        return False
    try:
        _fernet_instance.decrypt(val.encode("utf-8"))
        return True
    except Exception:
        return False
