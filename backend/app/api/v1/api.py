"""
Módulo central de enrutamiento para la versión 1 de la API.
Agrupa todos los sub-enrutadores (usuarios, productos, etc.) bajo un mismo prefijo.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, products, categories, movements, alerts, dashboard

api_router = APIRouter()

# ==========================================
# 🔐 SEGURIDAD Y ACCESO
# Rutas para manejo de sesiones y cuentas
# ==========================================
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])


# ==========================================
# 📦 CATÁLOGO E INVENTARIO PRINCIPAL
# Rutas para la gestión de productos físicos
# ==========================================
api_router.include_router(categories.router, prefix="/categories", tags=["Categorías"])
api_router.include_router(products.router, prefix="/products", tags=["Productos"])


# ==========================================
# 🔄 TRANSACCIONES Y MOVIMIENTOS
# Rutas para el flujo de entradas y salidas
# ==========================================
api_router.include_router(movements.router, prefix="/movements", tags=["Movimientos de Stock"])


# ==========================================
# 📊 MONITOREO Y PANEL DE CONTROL
# Rutas para estadísticas, métricas y avisos
# ==========================================
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alertas y Notificaciones"])