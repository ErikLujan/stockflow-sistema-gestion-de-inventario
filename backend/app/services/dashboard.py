"""
Módulo de servicios para el Dashboard.
Contiene la lógica para calcular las métricas y estadísticas del inventario
interactuando con múltiples entidades de la base de datos.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.category import Category

class DashboardService:
    """
    Clase de servicio que maneja la lógica de negocio para las métricas del dashboard.
    """

    @staticmethod
    def get_stats(db: Session) -> dict:
        """
        Calcula y retorna las estadísticas principales para el panel de administración.
        
        Realiza consultas agregadas para obtener el total de productos, alertas
        de stock y movimientos recientes.
        
        Args:
            db (Session): Sesión activa de base de datos inyectada desde el endpoint.
            
        Returns:
            dict: Un diccionario con las claves 'total_products', 'critical_stock','monthly_movements' y 'estimated_value'.
        """
        total_products = db.query(Product).filter(Product.is_active == True).count()
        critical_stock = db.query(Product).filter(
            Product.is_active == True, Product.current_stock <= Product.min_stock
        ).count()
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        monthly_movements = db.query(StockMovement).filter(StockMovement.created_at >= thirty_days_ago).count()

        total_volume = db.query(func.sum(Product.current_stock)).filter(Product.is_active == True).scalar()
        estimated_value = total_volume if total_volume else 0

        cat_stats = db.query(Category.name, func.count(Product.id))\
            .outerjoin(Product, Category.id == Product.category_id)\
            .group_by(Category.name).all()

        donut_labels = [row[0] for row in cat_stats if row[1] > 0]
        donut_series = [row[1] for row in cat_stats if row[1] > 0]

        today = datetime.now().date()
        dias_espanol = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        
        line_labels = []
        entradas = [0] * 7
        salidas = [0] * 7

        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            line_labels.append(dias_espanol[d.weekday()])

        seven_days_ago = today - timedelta(days=6)
        recent_movements = db.query(StockMovement).filter(
            StockMovement.created_at >= seven_days_ago
        ).all()

        for mov in recent_movements:
            delta_days = (today - mov.created_at.date()).days
            idx = 6 - delta_days
            
            if 0 <= idx <= 6:
                m_type = str(mov.movement_type).lower()
                if "compra" in m_type or "devolucion" in m_type:
                    entradas[idx] += mov.quantity
                elif "venta" in m_type:
                    salidas[idx] += mov.quantity

        return {
            "total_products": total_products,
            "critical_stock": critical_stock,
            "monthly_movements": monthly_movements,
            "estimated_value": estimated_value,
            "movements_chart": {
                "labels": line_labels,
                "entradas": entradas,
                "salidas": salidas
            },
            "category_chart": {
                "labels": donut_labels,
                "series": donut_series
            }
        }