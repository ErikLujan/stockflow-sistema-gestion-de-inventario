"""
Módulo que define el modelo ORM para la tabla de categorías.
Permite clasificar los productos del inventario.
"""
import uuid

from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.product import Product

class Category(Base):
    """
    Modelo ORM que representa una categoría de producto.
    """
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )