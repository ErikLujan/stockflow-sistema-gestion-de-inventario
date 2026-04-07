"""
Módulo de enrutamiento para alertas del sistema.
"""
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.core.rate_limit import limiter
from app.models.user import User
from app.repositories.product import ProductRepository
from app.services.notification import NotificationService

router = APIRouter()

@router.post(
    "/trigger-stock-check", 
    status_code=status.HTTP_200_OK,
    summary="Disparar manualmente la verificación y alertas de stock"
)
@limiter.limit("3/minute")
def trigger_stock_check(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Verifica el catálogo en busca de productos con stock crítico.
    Si encuentra alguno, dispara un correo electrónico de alerta.
    Requiere permisos de usuario autenticado.
    """
    low_stock_products = ProductRepository.get_low_stock_products(db)
    
    if not low_stock_products:
        return {"message": "El catálogo está sano. No hay productos con stock crítico."}

    emails_sent = 0
    for product in low_stock_products:
        success = NotificationService.send_low_stock_email(product)
        if success:
            emails_sent += 1

    return {
        "message": "Verificación completada.",
        "products_flagged": len(low_stock_products),
        "emails_sent": emails_sent
    }