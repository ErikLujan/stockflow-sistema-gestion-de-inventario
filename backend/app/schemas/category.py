"""
Módulo que define los esquemas Pydantic para la entidad Categoría.
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class CategoryBase(BaseModel):
    """
    Atributos base compartidos por todos los esquemas de categoría.
    """
    name: str = Field(..., min_length=2, max_length=100, description="Nombre de la categoría")
    description: Optional[str] = Field(None, max_length=255, description="Descripción opcional")

class CategoryCreate(CategoryBase):
    """
    Esquema para la creación de una nueva categoría.
    Hereda todos los campos de CategoryBase sin modificaciones.
    """
    pass

class CategoryUpdate(BaseModel):
    """
    Esquema para la actualización parcial de una categoría.
    Todos los campos son opcionales.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class CategoryResponse(CategoryBase):
    """
    Esquema de respuesta (DTO) devuelto al cliente.
    """
    id: UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)