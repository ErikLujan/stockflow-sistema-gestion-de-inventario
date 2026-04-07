"""
Módulo que define los esquemas Pydantic para el Dashboard.
Contiene los DTOs utilizados para transferir métricas y estadísticas del sistema.
"""
from pydantic import BaseModel, Field

class LineChartData(BaseModel):
    """Esquema para los datos del gráfico de líneas (Flujo de Inventario)."""
    labels: list[str] = Field(..., description="Etiquetas del eje X (ej. días de la semana)")
    entradas: list[int] = Field(..., description="Valores de las entradas de stock")
    salidas: list[int] = Field(..., description="Valores de las salidas de stock")

class DonutChartData(BaseModel):
    """Esquema para los datos del gráfico de dona (Inventario por Categoría)."""
    labels: list[str] = Field(..., description="Nombres de las categorías")
    series: list[int] = Field(..., description="Cantidad de productos por categoría")

class DashboardStats(BaseModel):
    """
    Esquema de respuesta (DTO) para las estadísticas principales del panel de control.
    """
    total_products: int = Field(
        ..., 
        description="Total de productos activos en el sistema"
    )
    critical_stock: int = Field(
        ..., 
        description="Cantidad de productos cuyo stock actual es menor o igual al mínimo permitido"
    )
    monthly_movements: int = Field(
        ..., 
        description="Cantidad de movimientos de inventario registrados en el mes en curso"
    )
    estimated_value: float = Field(
        default=0.0, 
        description="Valor monetario estimado del inventario actual"
    )
    movements_chart: LineChartData = Field(
        ..., 
        description="Datos estructurados para el gráfico semanal de entradas y salidas"
    )
    category_chart: DonutChartData = Field(
        ..., 
        description="Datos estructurados para la distribución de productos por categoría"
    )