"""
Módulo de repositorio para los Movimientos de Stock.
"""
from typing import Optional, Sequence, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.stock_movement import StockMovement, MovementType

class StockMovementRepository:
    """
    Repositorio para el historial auditable de inventario.
    Solo permite inserción y lectura, cumpliendo la regla de inmutabilidad.
    """

    @staticmethod
    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        type: Optional[MovementType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Sequence[StockMovement]:
        """
        Recupera el historial global de transacciones con filtros opcionales.
        """
        filters = []
        if type:
            filters.append(StockMovement.movement_type == type)
        if start_date:
            filters.append(StockMovement.created_at >= start_date)
        if end_date:
            filters.append(StockMovement.created_at <= end_date)

        stmt = select(StockMovement).where(and_(*filters))\
            .order_by(StockMovement.created_at.desc())\
            .offset(skip).limit(limit)

        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_by_product(
        db: Session, 
        product_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[StockMovement]:
        """
        Recupera el historial de movimientos de un producto específico, ordenado por fecha descendente.
        """
        stmt = select(StockMovement).where(
            StockMovement.product_id == product_id
        ).order_by(StockMovement.created_at.desc()).offset(skip).limit(limit)
        
        return db.execute(stmt).scalars().all()

    @staticmethod
    def create(
        db: Session, 
        obj_in: Dict[str, Any]
    ) -> StockMovement:
        """
        Inserta un nuevo registro de movimiento.
        """
        db_obj = StockMovement(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj