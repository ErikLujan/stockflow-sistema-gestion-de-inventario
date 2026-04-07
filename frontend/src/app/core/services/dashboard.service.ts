import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.development';
import { DashboardStats } from '../../shared/models/dashboard.model';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/dashboard`; 

  /**
   * Obtiene las estadísticas generales del sistema (productos totales, stock crítico, etc.).
   * * @returns {Observable<DashboardStats>} Observable que emite el DTO con las métricas calculadas.
   */
  getStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.apiUrl}/stats`);
  }
}