import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

/**
 * Interceptor HTTP que inyecta el token JWT en las cabeceras de cada petición saliente.
 * Además, captura globalmente los errores 401 (No Autorizado) para cerrar
 * la sesión automáticamente si el token ha expirado o es inválido.
 * * @param {HttpRequest<unknown>} req - La petición HTTP original.
 * @param {HttpHandlerFn} next - El siguiente manejador en la cadena de interceptores.
 * @returns {Observable<HttpEvent<unknown>>} Un observable con la petición modificada o el error capturado.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
    const authService = inject(AuthService);
    const token = authService.getToken();

    let authReq = req;
    if (token) {
        authReq = req.clone({
            setHeaders: { Authorization: `Bearer ${token}` }
        });
    }

    return next(authReq).pipe(
        catchError((error: HttpErrorResponse) => {
            if (error.status === 401) {
                console.warn('Sesión expirada o token inválido. Cerrando sesión automáticamente...');
                authService.logout();
            }
            return throwError(() => error);
        })
    );
};