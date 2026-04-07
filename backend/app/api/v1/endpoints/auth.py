"""
Módulo de enrutamiento para la autenticación y gestión de sesiones.
"""
import jwt

from fastapi import APIRouter, Depends, Request, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.dependencies.db import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.repositories.user import UserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.rate_limit import limiter
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión y obtener tokens")
@limiter.limit("5/minute")
def login(
    request: Request,
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Autentica a un usuario y le proporciona un token de acceso.
    Además, establece una cookie HttpOnly con el refresh token.
    
    Args:
        login_data (LoginRequest): DTO con email y contraseña.
        response (Response): Objeto de respuesta de FastAPI para inyectar cookies.
        db (Session): Sesión de base de datos inyectada.
        
    Returns:
        TokenResponse: DTO con el token de acceso de corta duración.
    """
    user = UserRepository.get_by_email(db, email=login_data.email)
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario está inactivo"
        )

    access_token = create_access_token(subject=user.id, role=user.role, email=user.email)
    refresh_token = create_refresh_token(subject=user.id)
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )

    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse, summary="Refrescar el token de acceso")
@limiter.limit("5/minute")
def refresh_token(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Genera un nuevo token de acceso utilizando un refresh token válido
    almacenado en las cookies (HttpOnly) del cliente.
    Implementa rotación de refresh tokens para mayor seguridad.
    
    Args:
        response (Response): Objeto de respuesta para inyectar la nueva cookie.
        refresh_token (str | None): El token extraído automáticamente de las cookies.
        db (Session): Sesión de base de datos.
        
    Raises:
        HTTPException: Si el token no está presente, es inválido o expiró.
        
    Returns:
        TokenResponse: DTO con el nuevo token de acceso.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token de actualización",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token no encontrado en las cookies"
        )
        
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id_str is None or token_type != "refresh":
            raise credentials_exception
            
        user_id = UUID(user_id_str)
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        raise credentials_exception
        
    user = UserRepository.get_by_id(db, user_id=user_id)
    
    if not user or not user.is_active:
        raise credentials_exception
        
    new_access_token = create_access_token(subject=user.id, role=user.role, email=user.email)
    new_refresh_token = create_refresh_token(subject=user.id)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    
    return TokenResponse(access_token=new_access_token)