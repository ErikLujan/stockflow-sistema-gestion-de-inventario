"""
Módulo que define el modelo ORM para la tabla de productos.
"""
import uuid

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.stock_movement import StockMovement

class Product(Base):
    """
    Modelo ORM que representa un producto en el inventario.
    Centraliza el estado del stock y la configuración de umbrales.
    """
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    sku: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(150), index=True, nullable=False
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True
    )

    unit_of_measure: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    current_stock: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    min_stock: Mapped[int] = mapped_column(
        Integer, default=10, nullable=False
    )

    supplier: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    category: Mapped["Category"] = relationship(back_populates="products")
    movements: Mapped[list["StockMovement"]] = relationship(back_populates="product")

    @property
    def category_name(self) -> str | None:
        """
        Propiedad calculada para obtener el nombre de la categoría automáticamente.
        """
        return self.category.name if self.category else None