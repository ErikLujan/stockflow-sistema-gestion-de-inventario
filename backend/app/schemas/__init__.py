"""
Módulo de inicialización de esquemas Pydantic.
Facilita la importación de esquemas desde otras partes de la aplicación.
"""
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.category import CategoryBase, CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.product import ProductBase, ProductCreate, ProductUpdate, ProductResponse
from app.schemas.stock_movement import StockMovementBase, StockMovementCreate, StockMovementResponse