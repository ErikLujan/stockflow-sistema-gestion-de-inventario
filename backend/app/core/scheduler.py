"""
Módulo de tareas programadas (Background Jobs).
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.api.dependencies.db import get_db
from app.repositories.product import ProductRepository
from app.services.notification import NotificationService

logger = logging.getLogger(__name__)

def check_stock_job() -> None:
    """
    Tarea ejecutada por el scheduler.
    Crea su propia sesión de base de datos ya que corre fuera del contexto de FastAPI.
    """
    logger.info("Iniciando tarea programada: Verificación de stock crítico...")
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        low_stock_products = ProductRepository.get_low_stock_products(db)
        for product in low_stock_products:
            NotificationService.send_low_stock_email(product)
        
        logger.info(f"Tarea finalizada. Se procesaron {len(low_stock_products)} productos en estado crítico.")
    except Exception as e:
        logger.error(f"Error en la tarea programada de stock: {e}")
    finally:
        db.close()

scheduler = BackgroundScheduler()

def start_scheduler() -> None:
    """
    Configura e inicia los trabajos programados.
    """
    if not scheduler.running:
        scheduler.add_job(
            check_stock_job, 
            trigger=CronTrigger(hour=8, minute=0), 
            id="daily_stock_check",
            replace_existing=True
        )
        scheduler.start()
        logger.info("Scheduler de tareas en segundo plano iniciado correctamente.")