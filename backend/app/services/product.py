"""
Módulo de servicios para la entidad Producto.
Implementa las reglas de negocio centrales del inventario.
"""
from typing import Sequence
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.product import ProductCreate, ProductUpdate
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.services.category import CategoryService

class ProductService:
    """
    Clase de servicio que maneja la lógica de negocio de los productos.
    """

    @staticmethod
    def get_product(db: Session, product_id: UUID) -> Product:
        """
        Recupera un producto por su ID validando su existencia.
        
        Raises:
            HTTPException: 404 si el producto no se encuentra.
        """
        product = ProductRepository.get_by_id(db, product_id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado."
            )
        return product

    @staticmethod
    def get_products(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Product]:
        """
        Recupera una lista paginada de productos.
        """
        return ProductRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def create_product(db: Session, product_in: ProductCreate) -> Product:
        """
        Valida y procesa la creación de un nuevo producto.
        Requiere un SKU único y una categoría existente.
        """
        existing_product = ProductRepository.get_by_sku(db, sku=product_in.sku)
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un producto registrado con este SKU."
            )
            
        CategoryService.get_category(db, category_id=product_in.category_id)
        
        return ProductRepository.create(db, obj_in=product_in.model_dump())

    @staticmethod
    def update_product(db: Session, product_id: UUID, product_in: ProductUpdate) -> Product:
        """
        Valida y procesa la actualización de un producto existente.
        """
        product = ProductService.get_product(db, product_id=product_id)
        update_data = product_in.model_dump(exclude_unset=True)
        
        if "category_id" in update_data and update_data["category_id"] != product.category_id:
            CategoryService.get_category(db, category_id=update_data["category_id"])
            
        return ProductRepository.update(db, db_obj=product, obj_in=update_data)
    
    @staticmethod
    def delete_product(db: Session, product_id: UUID) -> None:
        """
        Realiza una baja lógica (soft delete) del producto.
        """
        product = ProductService.get_product(db, product_id=product_id)
        product.is_active = False
        db.add(product)
        db.commit()