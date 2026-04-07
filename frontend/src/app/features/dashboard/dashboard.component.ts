import { Component, OnInit, inject, signal, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardService } from '../../core/services/dashboard.service';
import { DashboardStats } from '../../shared/models/dashboard.model';
import { NotificationService } from '../../core/services/notification.service';
import { toast } from 'ngx-sonner';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html'
})
export class DashboardComponent implements OnInit {
  private dashboardService = inject(DashboardService);
  private cdr = inject(ChangeDetectorRef);
  private notificationService = inject(NotificationService);

  isCheckingStock = signal<boolean>(false);

  stats = signal<DashboardStats | null>(null);
  isLoading = signal<boolean>(true);

  private lineChart: any;
  private donutChart: any;

  ngOnInit(): void {
    this.loadStats();
  }

  loadStats(): void {
    this.dashboardService.getStats().subscribe({
      next: (data) => {
        this.stats.set(data);
        this.isLoading.set(false);

        this.cdr.detectChanges();

        this.initCharts();
      },
      error: (err) => {
        console.error('Error cargando estadísticas', err);
        this.isLoading.set(false);
        this.cdr.detectChanges();
        this.initCharts();
      }
    });
  }

  initCharts(): void {
    this.renderLineChart();
    this.renderDonutChart();
  }

  renderLineChart(): void {
    const canvas = document.getElementById('lineChart') as HTMLCanvasElement;
    if (!canvas) return;

    if (this.lineChart) this.lineChart.destroy();

    this.lineChart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: this.stats()?.movements_chart.labels || [],
        datasets: [
          {
            label: 'Entradas',
            data: this.stats()?.movements_chart.entradas || [],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
          },
          {
            label: 'Salidas',
            data: this.stats()?.movements_chart.salidas || [],
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
              generateLabels: (chart: any) => {
                return chart.data.datasets.map((dataset: any, i: number) => {
                  const isHidden = !chart.isDatasetVisible(i);
                  return {
                    text: dataset.label,
                    fillStyle: isHidden ? 'transparent' : dataset.borderColor,
                    strokeStyle: isHidden ? '#4b5563' : dataset.borderColor,
                    fontColor: isHidden ? '#6b7280' : '#d1d5db',
                    lineWidth: 2,
                    pointStyle: 'circle',
                    datasetIndex: i
                  };
                });
              }
            },
            onClick: (e: any, legendItem: any, legend: any) => {
              const index = legendItem.datasetIndex;
              const chart = legend.chart;
              if (chart.isDatasetVisible(index)) {
                chart.hide(index);
              } else {
                chart.show(index);
              }
            }
          }
        },
        scales: {
          x: { grid: { color: '#374151', display: false }, ticks: { color: '#9ca3af' } },
          y: { grid: { color: '#374151' }, ticks: { color: '#9ca3af' }, border: { display: false } }
        }
      }
    });
  }

  renderDonutChart(): void {
    const canvas = document.getElementById('donutChart') as HTMLCanvasElement;
    if (!canvas) return;

    if (this.donutChart) this.donutChart.destroy();

    // Extraemos los datos reales que envió tu backend de Python
    const realLabels = this.stats()?.category_chart.labels || [];
    const realSeries = this.stats()?.category_chart.series || [];

    this.donutChart = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: realLabels,
        datasets: [{
          data: realSeries,
          backgroundColor: ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899', '#06b6d4', '#f43f5e'],
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '75%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 12,
              font: {
                size: 11
              },
              generateLabels: (chart: any) => {
                const data = chart.data;
                if (data.labels.length && data.datasets.length) {
                  return data.labels.map((label: string, i: number) => {
                    const meta = chart.getDatasetMeta(0);
                    const ds = data.datasets[0];
                    const isHidden = meta.data[i].hidden;

                    return {
                      text: label,
                      fillStyle: isHidden ? 'transparent' : ds.backgroundColor[i],
                      strokeStyle: isHidden ? '#4b5563' : ds.backgroundColor[i],
                      fontColor: isHidden ? '#6b7280' : '#d1d5db',
                      lineWidth: 2,
                      pointStyle: 'circle',
                      index: i
                    };
                  });
                }
                return [];
              }
            },
            onClick: (e: any, legendItem: any, legend: any) => {
              const index = legendItem.index;
              const chart = legend.chart;
              const meta = chart.getDatasetMeta(0);
              const dataPoint = meta.data[index];

              if (dataPoint.hidden) {
                dataPoint.hidden = false;
                chart.update();
              } else {
                dataPoint.hidden = true;
                chart.update();
              }
            }
          }
        }
      }
    });
  }

  /**
   * Ejecuta el chequeo manual de stock crítico.
   * Muestra notificaciones visuales sobre el proceso y el resultado.
   */
  checkAndSendAlerts(): void {
    this.isCheckingStock.set(true);
    toast.loading('Analizando catálogo y preparando alertas...', { id: 'stock-alert' });

    this.notificationService.triggerStockAlerts().subscribe({
      next: (response) => {
        this.isCheckingStock.set(false);

        if (response.products_flagged === 0) {
          toast.success('El catálogo está sano. No hay productos críticos.', { id: 'stock-alert' });
        } else {
          toast.success(
            `Se encontraron ${response.products_flagged} productos críticos. Se enviaron ${response.emails_sent} correos de alerta.`,
            { id: 'stock-alert' }
          );
        }
      },
      error: (err) => {
        this.isCheckingStock.set(false);
        if (err.status === 429) {
          toast.error('Has superado el límite de intentos. Por favor, espera un minuto.', { id: 'stock-alert' });
        } else {
          toast.error('Ocurrió un error al intentar verificar el stock.', { id: 'stock-alert' });
        }
        console.error('Error verificando stock:', err);
      }
    });
  }
}