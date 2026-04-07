"""
Módulo de enrutamiento para la gestión de categorías.
Expone los endpoints RESTful protegidos.
"""
from typing import Sequence
from uuid import UUID
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category import CategoryService
from app.models.user import User
from app.core.rate_limit import limiter

router = APIRouter()

@router.post(
    "/", 
    response_model=CategoryResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría"
)
@limiter.limit("5/minute")
def create_category(
    request: Request,
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CategoryResponse:
    """
    Crea una nueva categoría en el sistema.
    Requiere autenticación válida.
    """
    return CategoryService.create_category(db=db, category_in=category_in)

@router.get(
    "/", 
    response_model=list[CategoryResponse],
    summary="Listar todas las categorías"
)
@limiter.limit("60/minute")
def read_categories(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Sequence[CategoryResponse]:
    """
    Recupera una lista paginada de categorías.
    Requiere autenticación válida.
    """
    return CategoryService.get_categories(db=db, skip=skip, limit=limit)

@router.get(
    "/{category_id}", 
    response_model=CategoryResponse,
    summary="Obtener una categoría por ID"
)
@limiter.limit("60/minute")
def read_category(
    request: Request,
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CategoryResponse:
    """
    Recupera los detalles de una categoría específica.
    """
    return CategoryService.get_category(db=db, category_id=category_id)

@router.put(
    "/{category_id}", 
    response_model=CategoryResponse,
    summary="Actualizar una categoría"
)
@limiter.limit("5/minute")
def update_category(
    request: Request,
    category_id: UUID,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CategoryResponse:
    """
    Actualiza los datos de una categoría existente.
    """
    return CategoryService.update_category(db=db, category_id=category_id, category_in=category_in)

@router.delete(
    "/{category_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría (Soft Delete)"
)
@limiter.limit("10/minute")
def delete_category(
    request: Request,
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Da de baja una categoría sin eliminarla físicamente de la base de datos.
    """
    CategoryService.delete_category(db=db, category_id=category_id)