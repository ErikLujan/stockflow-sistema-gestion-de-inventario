"""
Módulo de repositorio para la entidad Producto.
Gestiona el acceso a datos del núcleo del inventario.
"""
from typing import Sequence, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product

class ProductRepository:
    """
    Clase repositorio que centraliza las operaciones CRUD para los productos.
    """

    @staticmethod
    def get_by_id(db: Session, product_id: UUID) -> Optional[Product]:
        """
        Busca un producto por su identificador único.
        Utiliza joinedload para cargar ansiosamente (eager load) la categoría asociada
        y evitar consultas N+1 en la serialización.
        
        Args:
            db (Session): Sesión activa de base de datos.
            product_id (UUID): El ID del producto a buscar.
            
        Returns:
            Optional[Product]: Instancia del producto si existe, None en caso contrario.
        """
        stmt = select(Product).options(joinedload(Product.category)).where(Product.id == product_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_by_sku(db: Session, sku: str) -> Optional[Product]:
        """
        Busca un producto por su código SKU (Stock Keeping Unit).
        """
        stmt = select(Product).where(Product.sku == sku)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Product]:
        """
        Recupera una lista paginada de productos, incluyendo sus categorías.
        """
        stmt = select(Product).options(joinedload(Product.category)).where(Product.is_active == True).offset(skip).limit(limit)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def create(db: Session, obj_in: Dict[str, Any]) -> Product:
        """
        Inserta un nuevo producto en la base de datos.
        El current_stock se inicializa en 0 por defecto según el modelo.
        """
        db_obj = Product(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, db_obj: Product, obj_in: Dict[str, Any]) -> Product:
        """
        Actualiza un producto existente. 
        Nota: La modificación de stock no debe pasar por aquí, sino por el módulo de movimientos.
        """
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get_low_stock_products(db: Session) -> Sequence[Product]:
        """
        Recupera todos los productos activos cuyo stock actual 
        ha caído por debajo o es igual a su umbral mínimo.
        """
        stmt = select(Product).where(
            Product.is_active == True,
            Product.current_stock <= Product.min_stock
        )
        return db.execute(stmt).scalars().all()