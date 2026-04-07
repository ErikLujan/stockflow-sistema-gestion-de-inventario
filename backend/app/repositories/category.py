"""
Módulo de repositorio para la entidad Categoría.
Aísla las operaciones de base de datos relativas a la clasificación de productos.
"""
from typing import Sequence, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.category import Category

class CategoryRepository:
    """
    Clase repositorio que centraliza las operaciones CRUD para las categorías.
    """

    @staticmethod
    def get_by_id(db: Session, category_id: UUID) -> Optional[Category]:
        """
        Busca una categoría por su identificador único.
        
        Args:
            db (Session): Sesión activa de base de datos.
            category_id (UUID): El ID de la categoría a buscar.
            
        Returns:
            Optional[Category]: Instancia de la categoría si existe, None en caso contrario.
        """
        stmt = select(Category).where(Category.id == category_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Category]:
        """
        Busca una categoría por su nombre exacto.
        Útil para validaciones de unicidad antes de crear.
        """
        stmt = select(Category).where(Category.name == name)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Category]:
        """
        Recupera una lista paginada de todas las categorías disponibles.
        """
        stmt = select(Category).where(Category.is_active == True).offset(skip).limit(limit)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def create(db: Session, obj_in: Dict[str, Any]) -> Category:
        """
        Inserta un nuevo registro de categoría en la base de datos.
        """
        db_obj = Category(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, db_obj: Category, obj_in: Dict[str, Any]) -> Category:
        """
        Actualiza los campos proporcionados de una categoría existente.
        """
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj