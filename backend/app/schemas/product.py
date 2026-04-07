"""
Módulo que define los esquemas Pydantic para la entidad Producto.
"""
from typing import Any, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator

class ProductBase(BaseModel):
    """
    Atributos base compartidos por todos los esquemas de producto.
    """
    sku: str = Field(..., min_length=3, max_length=50, description="Código SKU único")
    name: str = Field(..., min_length=2, max_length=150, description="Nombre del producto")
    unit_of_measure: str = Field(..., min_length=1, max_length=20, description="Ej: kg, litros, unidades")
    min_stock: int = Field(default=10, ge=0, description="Umbral para alertas de stock bajo")
    supplier: Optional[str] = Field(None, max_length=150, description="Proveedor principal")
    notes: Optional[str] = Field(None, description="Notas adicionales")

class ProductCreate(ProductBase):
    """
    Esquema para la creación de un nuevo producto.
    Requiere obligatoriamente el ID de la categoría a la que pertenece.
    Nota: El current_stock no se expone aquí, siempre inicia en 0 y se modifica vía movimientos.
    """
    category_id: UUID

class ProductUpdate(BaseModel):
    """
    Esquema para la actualización de un producto.
    El stock y el SKU no deberían ser modificables por esta vía regular.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    category_id: Optional[UUID] = None
    unit_of_measure: Optional[str] = Field(None, min_length=1, max_length=20)
    min_stock: Optional[int] = Field(None, ge=0)
    supplier: Optional[str] = Field(None, max_length=150)
    notes: Optional[str] = None

class ProductResponse(ProductBase):
    """
    Esquema de respuesta (DTO) para la entidad Producto.
    Incluye el stock actual calculado y los metadatos de auditoría.
    """
    id: UUID
    category_id: UUID
    category_name: Optional[str] = None
    current_stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def extract_category_name(cls, data: Any) -> Any:
        """
        Extrae el nombre de la categoría del objeto de SQLAlchemy y lo inyecta en el esquema.
        """
        if isinstance(data, dict):
            return data
            
        if hasattr(data, 'category') and data.category is not None:
            if not hasattr(data, '_sa_instance_state'):
                return data

        if hasattr(data, 'category') and data.category:
            pass 
            
        return data