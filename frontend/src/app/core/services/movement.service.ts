import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.development';
import { Movement } from '../../shared/models/movement.model';

@Injectable({
  providedIn: 'root'
})
export class MovementService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/movements`;

  /**
   * Obtiene el historial de movimientos de inventario, permitiendo filtrado desde el servidor.
   * * @param {string} [type] - Filtra por tipo de movimiento ('compra', 'venta', etc).
   * @param {string} [startDate] - Fecha de inicio en formato YYYY-MM-DD.
   * @param {string} [endDate] - Fecha de fin en formato YYYY-MM-DD.
   * @returns {Observable<Movement[]>} Observable que emite un arreglo de movimientos.
   */
  getMovements(type?: string, startDate?: string, endDate?: string): Observable<Movement[]> {
    let params = new HttpParams();

    if (type) {
      params = params.set('type', type);
    }

    if (startDate) {
      params = params.set('start_date', `${startDate}T00:00:00`);
    }

    if (endDate) {
      params = params.set('end_date', `${endDate}T23:59:59`);
    }

    return this.http.get<Movement[]>(this.apiUrl, { params });
  }

  /**
   * Registra una nueva transacción de inventario (Entrada o Salida).
   * Al registrarse con éxito, el backend debería actualizar automáticamente el stock del producto.
   * * @param {Partial<Movement>} movement - Objeto DTO con los detalles del movimiento.
   * @returns {Observable<Movement>} Observable que emite el movimiento persistido.
   */
  createMovement(movement: Partial<Movement>): Observable<Movement> {
    return this.http.post<Movement>(this.apiUrl, movement);
  }
}