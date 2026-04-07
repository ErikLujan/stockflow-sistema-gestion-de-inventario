export interface Product {
    id: string;
    sku: string;
    name: string;
    unit_of_measure: string;
    min_stock: number;
    supplier?: string;
    notes?: string;
    category_id: string;
    category_name?: string;
    current_stock: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface ProductResponse {
    total?: number;
}