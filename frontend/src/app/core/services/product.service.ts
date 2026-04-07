import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.development';
import { Product } from '../../shared/models/product.model';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/products`;

  constructor() { }

  /**
   * Solicita la lista completa de productos activos en el catálogo.
   * * @returns {Observable<Product[]>} Observable que emite un arreglo con las entidades de producto.
   */
  getProducts(): Observable<Product[]> {
    return this.http.get<Product[]>(this.apiUrl);
  }

  /**
   * Obtiene los datos de un producto específico mediante su identificador único.
   * * @param {string} id - El UUID del producto a consultar.
   * @returns {Observable<Product>} Observable que emite la información detallada del producto.
   */
  getProductById(id: string): Observable<Product> {
    return this.http.get<Product>(`${this.apiUrl}/${id}`);
  }

  /**
   * Envía la información capturada en el formulario para registrar un nuevo producto en la base de datos.
   * * @param {Partial<Product>} product - Objeto con los datos iniciales del producto (sin el ID).
   * @returns {Observable<Product>} Observable que emite la entidad del producto recién creado.
   */
  createProduct(product: Partial<Product>): Observable<Product> {
    return this.http.post<Product>(this.apiUrl, product);
  }

  /**
   * Sobrescribe los datos de un producto existente con nueva información.
   * * @param {string} id - El UUID del producto que se va a modificar.
   * @param {Partial<Product>} product - Objeto con los campos específicos que han sido actualizados.
   * @returns {Observable<Product>} Observable que emite la entidad del producto con los cambios aplicados.
   */
  updateProduct(id: string, product: Partial<Product>): Observable<Product> {
    return this.http.put<Product>(`${this.apiUrl}/${id}`, product);
  }

  /**
   * Ejecuta la eliminación (soft delete) de un producto del sistema.
   * * @param {string} id - El UUID del producto a dar de baja.
   * @returns {Observable<any>} Observable que emite la confirmación de la operación por parte del backend.
   */
  deleteProduct(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}