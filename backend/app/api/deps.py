from fastapi import Depends, HTTPException, status
from app.models.user import User, UserRole
from app.api.dependencies.auth import get_current_user

def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependencia de seguridad que verifica si el usuario autenticado
    tiene privilegios de administrador ('admin').
    
    Args:
        current_user (User): El usuario inyectado por la dependencia anterior.
        
    Raises:
        HTTPException: 403 Forbidden si el rol no es 'admin'.
        
    Returns:
        User: El objeto del usuario administrador validado.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes para realizar esta acción. Solo administradores."
        )
    return current_user