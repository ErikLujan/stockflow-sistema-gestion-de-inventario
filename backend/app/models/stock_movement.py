"""
Módulo que define el modelo ORM para los movimientos de stock.
Actúa como un libro mayor (ledger) inmutable para auditar el inventario.
"""
import uuid
import enum

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.product import Product

class MovementType(str, enum.Enum):
    """
    Enumeración estricta de los tipos de movimientos permitidos.
    """
    COMPRA = "compra"
    VENTA = "venta"
    AJUSTE = "ajuste"
    DEVOLUCION = "devolucion"

class StockMovement(Base):
    """
    Modelo ORM para registrar transacciones de inventario.
    Un registro aquí refleja una variación en el current_stock de un Producto.
    """
    __tablename__ = "stock_movements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    movement_type: Mapped[MovementType] = mapped_column(
        Enum(MovementType), nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    reason: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    external_reference: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship(back_populates="movements")