"""
Módulo que define el modelo ORM para la tabla de usuarios.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class UserRole(str, enum.Enum):
    """
    Enumeración para los roles de usuario permitidos en el sistema.
    Limita los valores posibles a nivel de código y base de datos.
    """
    ADMIN = "admin"
    USER = "user"

class User(Base):
    """
    Modelo ORM que representa a un usuario del sistema.
    Gestiona las credenciales de autenticación y el nivel de acceso (rol).
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False
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