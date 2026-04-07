"""
Módulo de enrutamiento para transacciones de inventario.
"""
from typing import Optional, Sequence, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, status, Request, Query
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.schemas.stock_movement import StockMovementCreate, StockMovementResponse
from app.services.stock_movement import StockMovementService
from app.models.stock_movement import MovementType
from app.models.user import User
from app.core.rate_limit import limiter

router = APIRouter()

@router.post(
    "/", 
    response_model=StockMovementResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un movimiento de stock"
)
@limiter.limit("20/minute")
def create_movement(
    request: Request,
    movement_in: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> StockMovementResponse:
    """
    Crea un nuevo registro auditable y actualiza el stock del producto de forma atómica.
    """
    return StockMovementService.create_movement(db=db, movement_in=movement_in, user_id=current_user.id)

@router.get("/", response_model=List[StockMovementResponse])
@limiter.limit("60/minute")
def get_all_stock_movements(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[MovementType] = Query(None, description="Filtrar por tipo de movimiento"),
    start_date: Optional[datetime] = Query(None, description="Fecha inicio (YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[datetime] = Query(None, description="Fecha fin (YYYY-MM-DDTHH:MM:SS)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtiene la lista de todos los movimientos de inventario registrados, con opciones de filtrado.
    """
    return StockMovementService.get_all_movements(
        db=db, skip=skip, limit=limit, type=type, start_date=start_date, end_date=end_date
    )

@router.get(
    "/product/{product_id}", 
    response_model=list[StockMovementResponse],
    summary="Obtener historial de un producto"
)
@limiter.limit("60/minute")
def read_product_movements(
    request: Request,
    product_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Sequence[StockMovementResponse]:
    """
    Devuelve el historial inmutable de movimientos para un producto específico.
    """
    return StockMovementService.get_product_movements(db=db, product_id=product_id, skip=skip, limit=limit)