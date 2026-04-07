import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.development';
import { User } from '../../shared/models/user.model';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/users/`;

  /**
   * Obtiene la lista completa de usuarios registrados en el sistema.
   * @returns {Observable<User[]>} Observable que emite un arreglo de usuarios.
   */
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl);
  }

  /**
   * Obtiene los detalles de un usuario específico por su ID.
   * @param {string} id - UUID del usuario.
   * @returns {Observable<User>} Observable que emite los datos del usuario.
   */
  getUser(id: string): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}${id}`);
  }

  /**
   * Envía la solicitud para registrar un nuevo usuario en el sistema.
   * Requiere que el token actual pertenezca a un Administrador.
   * * @param userData - Objeto con email, password y rol ('admin' | 'user').
   * @returns Observable con los datos del usuario creado.
   */
  createUser(userData: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, userData);
  }
  
  /**
   * Actualiza los datos de un usuario existente.
   * @param {string} id - UUID del usuario a actualizar.
   * @param {Partial<User>} userData - Datos a modificar.
   * @returns {Observable<User>} Observable que emite el usuario actualizado.
   */
  updateUser(id: string, userData: any): Observable<User> {
    return this.http.patch<User>(`${this.apiUrl}${id}`, userData);
  }

  /**
   * Elimina (o da de baja lógica) a un usuario del sistema.
   * @param {string} id - UUID del usuario a eliminar.
   * @returns {Observable<void>} Observable que indica la finalización de la operación.
   */
  deleteUser(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}`);
  }
}