export interface User {
    id: string;
    email: string;
    role: 'admin' | 'user';
    is_active: boolean;
    created_at: string;
    updated_at: string;
}