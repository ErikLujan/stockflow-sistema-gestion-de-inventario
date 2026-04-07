export interface DashboardStats {
    total_products: number;
    critical_stock: number;
    monthly_movements: number;
    estimated_value: number;
    movements_chart: {
        labels: string[];
        entradas: number[];
        salidas: number[];
    };
    category_chart: {
        labels: string[];
        series: number[];
    };
}