"""
Módulo de inyección de dependencias para la autenticación y autorización.
Valida los tokens JWT y recupera el usuario actual de la sesión.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from uuid import UUID

from app.core.config import settings
from app.api.dependencies.db import get_db
from app.models.user import User
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependencia central para proteger endpoints.
    Verifica la firma y expiración del JWT, y valida que el usuario exista y esté activo.
    
    Args:
        db (Session): Sesión de base de datos inyectada.
        token (str): Token JWT extraído de las cabeceras de la petición.
        
    Raises:
        HTTPException: Si el token es inválido, expiró, o el usuario no existe/está inactivo.
        
    Returns:
        User: Instancia del modelo del usuario autenticado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        user_id = UUID(user_id_str)
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        raise credentials_exception

    user = UserRepository.get_by_id(db, user_id=user_id)
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El usuario está inactivo"
        )
        
    return user