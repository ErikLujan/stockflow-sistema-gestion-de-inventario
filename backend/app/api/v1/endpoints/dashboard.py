from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.core.rate_limit import limiter
from app.schemas.dashboard import DashboardStats
from app.services.dashboard import DashboardService

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
@limiter.limit("60/minute")
def get_dashboard_stats(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> DashboardStats:
    """
    Obtiene las métricas calculadas para el panel de administración.
    
    Requiere autenticación mediante token JWT activo.
    
    Args:
        db (Session): Sesión de base de datos proporcionada por inyección de dependencias.
        current_user (User): Entidad del usuario logueado actualmente que hace la petición.
        
    Returns:
        DashboardStats: DTO con las métricas consolidadas del sistema (Totales, alertas, etc.).
    """
    return DashboardService.get_stats(db=db)