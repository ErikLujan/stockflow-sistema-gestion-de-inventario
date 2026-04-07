"""
Módulo de enrutamiento para la gestión de productos.
"""
from typing import Sequence
from uuid import UUID
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product import ProductService
from app.models.user import User
from app.core.rate_limit import limiter

router = APIRouter()

@router.post(
    "/", 
    response_model=ProductResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto"
)
@limiter.limit("5/minute")
def create_product(
    request: Request,
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ProductResponse:
    """
    Registra un nuevo producto en el catálogo.
    Requiere autenticación válida.
    """
    return ProductService.create_product(db=db, product_in=product_in)

@router.get(
    "/", 
    response_model=list[ProductResponse],
    summary="Listar todos los productos"
)
@limiter.limit("60/minute")
def read_products(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Sequence[ProductResponse]:
    """
    Recupera una lista paginada de todos los productos.
    """
    return ProductService.get_products(db=db, skip=skip, limit=limit)

@router.get(
    "/{product_id}", 
    response_model=ProductResponse,
    summary="Obtener un producto por ID"
)
@limiter.limit("60/minute")
def read_product(
    request: Request,
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ProductResponse:
    """
    Busca y devuelve los datos de un producto específico.
    """
    return ProductService.get_product(db=db, product_id=product_id)

@router.put(
    "/{product_id}", 
    response_model=ProductResponse,
    summary="Actualizar un producto"
)
@limiter.limit("5/minute")
def update_product(
    request: Request,
    product_id: UUID,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ProductResponse:
    """
    Modifica la información de un producto. 
    Nota: El stock no se altera mediante este endpoint.
    """
    return ProductService.update_product(db=db, product_id=product_id, product_in=product_in)

@router.delete(
    "/{product_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un producto (Soft Delete)"
)
@limiter.limit("10/minute")
def delete_product(
    request: Request,
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Da de baja un producto sin eliminarlo físicamente para preservar el historial auditable.
    """
    ProductService.delete_product(db=db, product_id=product_id)