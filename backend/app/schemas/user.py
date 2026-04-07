"""
Módulo que define los esquemas Pydantic para la validación de datos de Usuario.
Implementa el patrón DTO (Data Transfer Object) para separar la capa ORM de la capa API.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """
    Esquema base con los atributos comunes compartidos por otros esquemas de usuario.
    """
    email: EmailStr
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """
    Esquema para la creación de un nuevo usuario desde el cliente.
    Requiere la contraseña en texto plano, la cual será hasheada posteriormente en la capa de servicio.
    """
    password: str = Field(min_length=8, description="La contraseña debe tener al menos 8 caracteres")
    role: Optional[UserRole] = UserRole.USER


class UserUpdate(BaseModel):
    """
    Esquema para la actualización de un usuario existente.
    Todos los campos son opcionales para permitir actualizaciones parciales (PATCH).
    """
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    """
    Esquema de respuesta (DTO) que se devuelve al cliente de forma segura.
    Excluye explícitamente la contraseña y expone los metadatos generados por la base de datos.
    """
    id: UUID
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)