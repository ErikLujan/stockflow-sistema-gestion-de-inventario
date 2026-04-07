import { Product } from './product.model';

export interface Movement {
    id: string;
    product_id: string;
    movement_type: 'compra' | 'venta' | 'devolucion' | 'ajuste';
    quantity: number;
    reason?: string;
    created_at: string;
    product?: Product; 
}