"""
Módulo que define los esquemas Pydantic para los Movimientos de Stock.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.stock_movement import MovementType

class StockMovementBase(BaseModel):
    """
    Atributos base para un movimiento de inventario.
    """
    product_id: UUID = Field(..., description="ID del producto afectado")
    movement_type: MovementType = Field(..., description="Tipo de movimiento (compra, venta, ajuste, devolucion)")
    quantity: int = Field(..., description="Cantidad involucrada. Para ajustes puede ser negativa.")
    reason: Optional[str] = Field(None, max_length=255, description="Motivo del movimiento")
    external_reference: Optional[str] = Field(None, max_length=100, description="Nº de factura, remito u orden")

class StockMovementCreate(StockMovementBase):
    """
    Esquema para registrar un nuevo movimiento.
    Nota: El user_id no se incluye aquí porque se inyectará de forma segura desde el token JWT.
    """
    pass

class StockMovementResponse(StockMovementBase):
    """
    Esquema de respuesta (DTO) devuelto al cliente.
    """
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)