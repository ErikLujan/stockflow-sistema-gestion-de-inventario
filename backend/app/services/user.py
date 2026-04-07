"""
Módulo de servicios para la entidad Usuario.
Contiene la lógica de negocio y orquesta las llamadas al repositorio y utilidades de seguridad.
"""
from typing import Sequence
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.user import UserCreate
from app.models.user import User
from app.repositories.user import UserRepository
from app.core.security import get_password_hash

class UserService:
    """
    Clase de servicio que maneja la lógica de negocio relacionada con la gestión de usuarios.
    """

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """
        Obtiene la lista de todos los usuarios del sistema.
        """
        return UserRepository.get_all(db, skip=skip, limit=limit)
    
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        """
        Valida y procesa la creación de un nuevo usuario.
        
        Args:
            db (Session): Sesión activa de base de datos inyectada desde el endpoint.
            user_in (UserCreate): DTO con los datos de entrada validados por Pydantic.
            
        Raises:
            HTTPException: Si el correo electrónico ya se encuentra registrado.
            
        Returns:
            User: La entidad de usuario persistida.
        """
        existing_user = UserRepository.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ingresado ya está registrado en el sistema."
            )
        
        hashed_password = get_password_hash(user_in.password)
        
        user_data = user_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_password
        
        return UserRepository.create(db, obj_in=user_data)
    
    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> None:
        """
        Verifica que el usuario exista y procede a eliminarlo.
        """
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario que intentas eliminar no existe."
            )
        
        UserRepository.delete(db, user_id)