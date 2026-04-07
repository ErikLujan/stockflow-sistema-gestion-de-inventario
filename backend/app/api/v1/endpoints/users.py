"""
Módulo de enrutamiento para la gestión de usuarios.
Expone los endpoints RESTful protegidos y validados.
"""
from typing import List, Sequence
from uuid import UUID
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService
from app.api.dependencies.db import get_db
from app.api.deps import get_current_active_admin
from app.models.user import User
from app.core.rate_limit import limiter

router = APIRouter()

@router.get(
    "/", 
    response_model=List[UserResponse],
    summary="Listar todos los usuarios (Solo Admins)"
)
@limiter.limit("60/minute")
def read_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_active_admin)
) -> Sequence[UserResponse]:
    """
    Recupera la lista completa de usuarios. 
    Requiere privilegios de administrador.
    """
    return UserService.get_all_users(db=db, skip=skip, limit=limit)

@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Obtener perfil del usuario actual"
)
@limiter.limit("60/minute")
def read_users_me(
    request: Request,
    current_user: User = Depends(get_current_active_admin)
) -> UserResponse:
    """
    Recupera los detalles del usuario actualmente autenticado.
    Este endpoint está protegido y requiere un JWT de acceso válido.
    
    Args:
        current_user (User): Instancia del usuario inyectada por la dependencia de seguridad.
        
    Returns:
        UserResponse: DTO con los datos del perfil del usuario.
    """
    return current_user

@router.post(
    "/", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario"
)
@limiter.limit("5/minute")
def create_user(
    request: Request, 
    user_in: UserCreate, 
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Crea un nuevo usuario en el sistema.
    
    Aplica limitación de tasa (60 peticiones por minuto por IP) para mitigar 
    creación automatizada de cuentas y abusos del servicio.
    
    Args:
        request (Request): Objeto de petición nativo de FastAPI, requerido por slowapi.
        user_in (UserCreate): DTO con los datos de creación validados.
        db (Session): Sesión de base de datos inyectada.
        
    Returns:
        UserResponse: DTO con los datos del usuario creado, omitiendo datos sensibles.
    """
    return UserService.create_user(db=db, user_in=user_in)

@router.delete(
    "/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un usuario (Solo Admins)"
)
@limiter.limit("10/minute")
def delete_user(
    request: Request,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_active_admin)
) -> None:
    """
    Elimina un usuario del sistema mediante su ID.
    Requiere privilegios de administrador.
    """
    UserService.delete_user(db=db, user_id=user_id)