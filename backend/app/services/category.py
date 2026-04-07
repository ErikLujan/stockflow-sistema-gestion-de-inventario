"""
Módulo de servicios para la entidad Categoría.
Orquesta las operaciones de negocio, incluyendo validaciones de unicidad,
antes de interactuar con la capa de persistencia.
"""
from typing import Sequence
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.category import CategoryCreate, CategoryUpdate
from app.models.category import Category
from app.repositories.category import CategoryRepository

class CategoryService:
    """
    Clase de servicio que maneja la lógica de negocio de las categorías.
    """

    @staticmethod
    def get_category(db: Session, category_id: UUID) -> Category:
        """
        Recupera una categoría por su ID validando su existencia.
        
        Raises:
            HTTPException: 404 si la categoría no se encuentra en la base de datos.
        """
        category = CategoryRepository.get_by_id(db, category_id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada."
            )
        return category

    @staticmethod
    def get_categories(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Category]:
        """
        Recupera una lista paginada de categorías.
        """
        return CategoryRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def create_category(db: Session, category_in: CategoryCreate) -> Category:
        """
        Valida y procesa la creación de una nueva categoría.
        Asegura que no existan dos categorías con el mismo nombre.
        """
        existing_category = CategoryRepository.get_by_name(db, name=category_in.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría registrada con este nombre."
            )
            
        return CategoryRepository.create(db, obj_in=category_in.model_dump())

    @staticmethod
    def update_category(db: Session, category_id: UUID, category_in: CategoryUpdate) -> Category:
        """
        Valida y procesa la actualización de una categoría existente.
        """
        category = CategoryService.get_category(db, category_id=category_id)
        update_data = category_in.model_dump(exclude_unset=True)
        
        if "name" in update_data and update_data["name"] != category.name:
            existing_category = CategoryRepository.get_by_name(db, name=update_data["name"])
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nuevo nombre de categoría ya está en uso."
                )
                
        return CategoryRepository.update(db, db_obj=category, obj_in=update_data)
    
    @staticmethod
    def delete_category(db: Session, category_id: UUID) -> None:
        """
        Realiza una baja lógica (soft delete) de la categoría.
        """
        category = CategoryService.get_category(db, category_id=category_id)
        category.is_active = False
        db.add(category)
        db.commit()