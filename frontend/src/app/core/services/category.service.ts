import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Category } from '../../shared/models/category.model';

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/categories`;

  /**
   * Obtiene la lista completa de categorías desde el servidor.
   * * @returns {Observable<Category[]>} Un observable que emite un array de categorías.
   */
  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(this.apiUrl);
  }

  /**
   * Obtiene una categoría específica por su identificador único.
   * * @param {string} id - El UUID de la categoría a buscar.
   * @returns {Observable<Category>} Un observable que emite la entidad categoría encontrada.
   */
  getCategoryById(id: string): Observable<Category> {
    return this.http.get<Category>(`${this.apiUrl}/${id}`);
  }

  /**
   * Envía los datos para crear una nueva categoría en el sistema.
   * * @param {Partial<Category>} category - Objeto DTO con los datos de la nueva categoría.
   * @returns {Observable<Category>} Un observable que emite la categoría recién creada.
   */
  createCategory(category: Partial<Category>): Observable<Category> {
    return this.http.post<Category>(this.apiUrl, category);
  }

  /**
   * Envía los datos actualizados de una categoría existente.
   * * @param {string} id - El UUID de la categoría a modificar.
   * @param {Partial<Category>} category - Objeto DTO con los campos a actualizar.
   * @returns {Observable<Category>} Un observable que emite la categoría actualizada.
   */
  updateCategory(id: string, category: Partial<Category>): Observable<Category> {
    return this.http.put<Category>(`${this.apiUrl}/${id}`, category);
  }

  /**
   * Realiza la eliminación (física o lógica, según backend) de una categoría.
   * * @param {string} id - El UUID de la categoría a eliminar.
   * @returns {Observable<any>} Un observable que emite la respuesta de la operación.
   */
  deleteCategory(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}