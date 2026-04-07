"""
Módulo de servicios para los Movimientos de Stock.
Aplica las reglas matemáticas sobre el inventario y asegura la atomicidad.
"""
from typing import Optional, Sequence
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.stock_movement import StockMovementCreate
from app.models.stock_movement import StockMovement, MovementType
from app.repositories.stock_movement import StockMovementRepository
from app.services.product import ProductService

class StockMovementService:
    """
    Clase de servicio que maneja la lógica de entradas y salidas.
    """

    @staticmethod
    def get_all_movements(db: Session, skip: int = 0, limit: int = 100,type: Optional[MovementType] = None,start_date: Optional[datetime] = None,end_date: Optional[datetime] = None) -> Sequence[StockMovement]:
        """
        Obtiene el historial global de transacciones de inventario con filtros.
        
        Args:
            db (Session): Sesión activa de base de datos.
            skip (int): Número de registros a omitir (paginación).
            limit (int): Límite máximo de registros a retornar.
            type (Optional[MovementType]): Filtro por tipo de movimiento.
            start_date (Optional[datetime]): Fecha de inicio para el filtro de fecha.
            end_date (Optional[datetime]): Fecha de fin para el filtro de fecha.
            
        Returns:
            Sequence[StockMovement]: Lista de todos los movimientos registrados.
        """
        return StockMovementRepository.get_all(
            db=db, skip=skip, limit=limit, type=type, start_date=start_date, end_date=end_date
        )

    @staticmethod
    def get_product_movements(db: Session, product_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[StockMovement]:
        """
        Valida que el producto exista y devuelve su historial.
        """
        ProductService.get_product(db, product_id=product_id)
        return StockMovementRepository.get_by_product(db, product_id=product_id, skip=skip, limit=limit)

    @staticmethod
    def create_movement(db: Session, movement_in: StockMovementCreate, user_id: UUID) -> StockMovement:
        """
        Procesa una transacción de inventario.
        Actualiza el current_stock del producto y registra el movimiento auditable.
        """
        product = ProductService.get_product(db, product_id=movement_in.product_id)
        
        delta = movement_in.quantity
        if movement_in.movement_type == MovementType.VENTA:
            delta = -abs(movement_in.quantity)
        elif movement_in.movement_type in (MovementType.COMPRA, MovementType.DEVOLUCION):
            delta = abs(movement_in.quantity)

        new_stock = product.current_stock + delta

        if new_stock < 0 and movement_in.movement_type == MovementType.VENTA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Stock actual: {product.current_stock}"
            )

        movement_data = movement_in.model_dump()
        movement_data["user_id"] = user_id
        
        try:
            product.current_stock = new_stock
            db.add(product)
            
            return StockMovementRepository.create(db, obj_in=movement_data)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al procesar la transacción de inventario."
            )