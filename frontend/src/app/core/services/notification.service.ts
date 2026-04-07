import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment.development';
import { Observable } from 'rxjs';

/**
 * Servicio para gestionar las alertas y notificaciones del sistema.
 * Se comunica con los endpoints del backend para disparar correos electrónicos.
 */
@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  /**
   * Dispara el chequeo manual de stock en el backend.
   * Si hay productos en estado crítico, el backend enviará los correos
   * configurados vía Brevo.
   * * @returns Observable con el resultado de la operación.
   */
  triggerStockAlerts(): Observable<{ message: string, products_flagged: number, emails_sent: number }> {
    return this.http.post<{ message: string, products_flagged: number, emails_sent: number }>(
      `${this.apiUrl}/alerts/trigger-stock-check`,
      {}
    );
  }
}