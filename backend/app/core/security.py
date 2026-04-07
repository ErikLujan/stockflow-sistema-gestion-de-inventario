"""
Módulo de seguridad principal.
Maneja el hashing y la verificación de contraseñas utilizando bcrypt,
asegurando que las credenciales nunca se expongan ni se almacenen en texto plano.
"""
import bcrypt
import jwt

from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from app.core.config import settings

ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su versión hasheada.
    
    Args:
        plain_password (str): La contraseña provista por el usuario.
        hashed_password (str): El hash almacenado en la base de datos.
        
    Returns:
        bool: True si coinciden, False en caso contrario.
    """
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hash_bytes)

def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro a partir de una contraseña en texto plano.
    
    Args:
        password (str): La contraseña en texto plano a cifrar.
        
    Returns:
        str: El string hasheado resultante.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
    
    return hashed_password_bytes.decode('utf-8')

def create_access_token(subject: str | Any, role: str, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un JSON Web Token (JWT) de acceso de corta duración.
    
    Args:
        subject (str | Any): El identificador del usuario (generalmente el UUID como string).
        expires_delta (Optional[timedelta]): Tiempo personalizado de expiración. Si es None, usa el valor por defecto de la configuración.

    Returns:
        str: El token JWT codificado.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "email": email}

    if role:
        to_encode["role"] = role
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str | Any) -> str:
    """
    Genera un JWT de actualización (Refresh Token) de mayor duración (ej. 7 días).
    Este token no debe exponerse al frontend, sino enviarse en una cookie HttpOnly.
    
    Args:
        subject (str | Any): El identificador del usuario.
        
    Returns:
        str: El token JWT codificado.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)