import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment.development';
import { BehaviorSubject, Observable, tap } from 'rxjs';

export interface LoginData {
    email: string;
    password: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private http = inject(HttpClient);
    private router = inject(Router);
    private apiUrl = environment.apiUrl;

    private loggedIn = new BehaviorSubject<boolean>(this.hasToken());
    public isLoggedIn$ = this.loggedIn.asObservable();

    isAuthenticated = signal<boolean>(this.hasToken());

    constructor() { }

    /**
         * Envía las credenciales al backend en formato JSON puro.
         * Al recibir una respuesta exitosa, guarda el token y actualiza el estado de la sesión.
         * @param {LoginData} data - Objeto que contiene el correo y la contraseña.
         * @returns {Observable<TokenResponse>} Observable con el token de acceso.
         */
    login(data: LoginData): Observable<TokenResponse> {
        return this.http.post<TokenResponse>(`${this.apiUrl}/auth/login`, data)
            .pipe(
                tap(response => {
                    this.setToken(response.access_token);
                    this.loggedIn.next(true);
                    this.isAuthenticated.set(true);
                })
            );
    }

    /**
     * Finaliza la sesión actual eliminando el token del almacenamiento local,
     * emitiendo un estado de sesión falso a los suscriptores y redirigiendo al login.
     * * @returns {void}
     */
    logout(): void {
        localStorage.removeItem('access_token');
        this.loggedIn.next(false);
        this.isAuthenticated.set(false);
        this.router.navigate(['/login']);
    }

    /**
     * Almacena el token JWT en el LocalStorage del navegador web.
     * * @private
     * @param {string} token - El string del JSON Web Token generado por el backend.
     * @returns {void}
     */
    private setToken(token: string): void {
        localStorage.setItem('access_token', token);
    }

    /**
     * Recupera el token JWT almacenado actualmente en el navegador.
     * * @returns {string | null} El token como cadena de texto, o null si no existe.
     */
    public getToken(): string | null {
        return localStorage.getItem('access_token');
    }

    /**
     * Verifica la existencia de un token guardado. 
     * Es útil para inicializar el estado de la aplicación o para interceptores.
     * * @private
     * @returns {boolean} True si existe un token en el almacenamiento, False en caso contrario.
     */
    private hasToken(): boolean {
        return !!this.getToken();
    }

    /**
     * Extrae y decodifica el payload del JWT de forma nativa.
     * @private
     * @returns {any | null} El objeto JSON con los datos del token, o null si falla.
     */
    private getDecodedToken(): any | null {
        const token = this.getToken();
        if (!token) return null;

        try {
            const payloadBase64 = token.split('.')[1];
            const decodedJson = atob(payloadBase64);
            return JSON.parse(decodedJson);
        } catch (error) {
            console.error('Error al decodificar el token JWT:', error);
            return null;
        }
    }

    /**
     * Obtiene el rol del usuario logueado leyendo el payload del token.
     * @returns {string | null} El rol del usuario ('admin' o 'user') o null.
     */
    public getUserRole(): string | null {
        const decodedToken = this.getDecodedToken();
        return decodedToken ? decodedToken.role : null;
    }

    /**
     * Obtiene el correo electrónico del usuario logueado leyendo el payload del token.
     * Verifica el claim estándar 'sub' (Subject) o un claim explícito 'email'.
     * @returns {string | null} El email del usuario o null si no se encuentra.
     */
    public getUserEmail(): string | null {
        const decodedToken = this.getDecodedToken();
        if (!decodedToken) return null;

        return decodedToken.email || decodedToken.sub || null;
    }
}