import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login.component';
import { authGuard } from './core/guards/auth.guard';
import { adminGuard } from './core/guards/admin.guard';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { ProductListComponent } from './features/products/product-list/product-list.component';
import { ProductFormComponent } from './features/products/product-form/product-form.component';
import { UserListComponent } from './features/user-list/user-list.component';

export const routes: Routes = [
    { 
        path: 'login', 
        component: LoginComponent,
        title: 'StockFlow | Iniciar Sesión'
    },
    {
        path: '',
        component: MainLayoutComponent,
        canActivate: [authGuard],
        children: [
            { 
                path: 'dashboard', 
                component: DashboardComponent,
                title: 'StockFlow | Dashboard'
            },
            { 
                path: 'productos', 
                component: ProductListComponent,
                title: 'StockFlow | Productos'
            },
            { 
                path: 'productos/nuevo', 
                component: ProductFormComponent,
                title: 'StockFlow | Nuevo Producto'
            },
            { 
                path: 'productos/editar/:id', 
                component: ProductFormComponent,
                title: 'StockFlow | Editar Producto'
            },
            { 
                path: 'categorias', 
                loadComponent: () => import('./features/categories/category-list/category-list.component').then(m => m.CategoryListComponent),
                title: 'StockFlow | Categorías'
            },
            { 
                path: 'movimientos', 
                loadComponent: () => import('./features/movements/movement-list/movement-list.component').then(m => m.MovementListComponent),
                title: 'StockFlow | Movimientos'
            },
            { 
                path: 'usuarios', 
                component: UserListComponent, 
                canActivate: [adminGuard],
                title: 'StockFlow | Gestión de Usuarios'
            },
            { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
        ]
    },
    { path: '**', redirectTo: '/login' }
];