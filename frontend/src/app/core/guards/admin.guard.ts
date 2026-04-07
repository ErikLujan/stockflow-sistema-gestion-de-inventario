import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const adminGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    const role = authService.getUserRole();

    if (role?.toLowerCase() === 'admin') {
        return true;
    } else {
        router.navigate(['/dashboard']);
        return false;
    }
};