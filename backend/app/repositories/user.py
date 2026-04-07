"""
Módulo de repositorio para la entidad Usuario.
Aísla todas las consultas directas a la base de datos (SQLAlchemy) del resto de la aplicación.
"""
from typing import Sequence, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User

class UserRepository:
    """
    Clase repositorio que centraliza las operaciones CRUD de base de datos para usuarios.
    """

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """
        Recupera una lista paginada de todos los usuarios registrados.
        """
        stmt = select(User).offset(skip).limit(limit)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """
        Busca un usuario por su identificador único (UUID).
        
        Args:
            db (Session): Sesión activa de base de datos.
            user_id (UUID): El identificador único del usuario.
            
        Returns:
            Optional[User]: Instancia del modelo User si existe, de lo contrario None.
        """
        stmt = select(User).where(User.id == user_id)
        return db.execute(stmt).scalar_one_or_none()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """
        Busca un usuario por su dirección de correo electrónico.
        
        Args:
            db (Session): Sesión activa de base de datos.
            email (str): Correo electrónico a buscar.
            
        Returns:
            Optional[User]: Instancia del modelo User si existe, de lo contrario None.
        """
        stmt = select(User).where(User.email == email)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(db: Session, obj_in: Dict[str, Any]) -> User:
        """
        Inserta un nuevo registro de usuario en la base de datos.
        
        Args:
            db (Session): Sesión activa de base de datos.
            obj_in (Dict[str, Any]): Diccionario con los datos validados del usuario.
            
        Returns:
            User: La instancia del modelo User recién creada y persistida.
        """
        db_obj = User(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, user_id: UUID) -> None:
        """
        Elimina físicamente un usuario de la base de datos.
        """
        user = UserRepository.get_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()