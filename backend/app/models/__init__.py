"""
Módulo de inicialización de modelos.
Importar todos los modelos aquí asegura que Alembic los detecte
al leer Base.metadata durante la generación de migraciones.
"""
from app.models.base import Base
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.stock_movement import StockMovement