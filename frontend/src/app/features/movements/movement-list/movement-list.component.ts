import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MovementService } from '../../../core/services/movement.service';
import { ProductService } from '../../../core/services/product.service';
import { Movement } from '../../../shared/models/movement.model';
import { Product } from '../../../shared/models/product.model';
import { ExportService } from '../../../core/services/export.service';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-movement-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './movement-list.component.html'
})
export class MovementListComponent implements OnInit {
  private movementService = inject(MovementService);
  private productService = inject(ProductService);
  private exportService = inject(ExportService);
  private fb = inject(FormBuilder);

  // --- Estados de la Vista ---
  movements = signal<Movement[]>([]);
  products = signal<Product[]>([]);
  isLoading = signal<boolean>(true);
  error = signal<string | null>(null);

  // --- Estados de filtro ---
  filterType = signal<string>('');
  filterStartDate = signal<string>('');
  filterEndDate = signal<string>('');

  // --- Estados del Modal ---
  isModalOpen = signal<boolean>(false);
  isSaving = signal<boolean>(false);

  // --- Estados del Nuevo Modal de Vista de Notas ---
  isNotesModalOpen = signal<boolean>(false);
  currentNotesToView = signal<string | null>(null);

  movementForm: FormGroup = this.fb.group({
    product_id: ['', [Validators.required]],
    movement_type: ['', [Validators.required]],
    quantity: [1, [Validators.required, Validators.min(1)]],
    reason: ['', [Validators.maxLength(250)]]
  });

  // --- Estados de Paginación ---
  currentPage = signal<number>(1);
  itemsPerPage = signal<number>(6);

  // Señal computada: extrae solo los movimientos de la página actual
  paginatedMovements = computed(() => {
    const start = (this.currentPage() - 1) * this.itemsPerPage();
    const end = start + this.itemsPerPage();
  
    return this.movements().slice(start, end); 
  });

  // Señal computada: calcula el total de páginas
  totalPages = computed(() => {
    return Math.ceil(this.movements().length / this.itemsPerPage()) || 1;
  });

  // Métodos de navegación
  nextPage(): void {
    if (this.currentPage() < this.totalPages()) {
      this.currentPage.update(p => p + 1);
    }
  }

  prevPage(): void {
    if (this.currentPage() > 1) {
      this.currentPage.update(p => p - 1);
    }
  }

  /**
   * Inicializa el componente. Dispara la carga paralela del historial de movimientos
   * y el catálogo de productos activos.
   * * @returns {void}
   */
  ngOnInit(): void {
    this.loadMovements();
    this.loadProducts();
  }

  /**
   * Consume el servicio para obtener el historial de movimientos y actualizar la tabla.
   * * @returns {void}
   */
  loadMovements(): void {
    this.isLoading.set(true);
    this.error.set(null);

    const type = this.filterType();
    const start = this.filterStartDate();
    const end = this.filterEndDate();

    this.movementService.getMovements(type, start, end).subscribe({
      next: (data) => {
        this.movements.set(data);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Error cargando movimientos:', err);
        this.error.set('No se pudo cargar el historial de movimientos.');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Actualiza el tipo de movimiento seleccionado y recarga la tabla.
   */
  onFilterTypeChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    this.filterType.set(select.value);
    this.loadMovements(); // Recargamos instantáneamente
  }

  /**
   * Actualiza la fecha de inicio.
   */
  onStartDateChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.filterStartDate.set(input.value);
  }

  /**
   * Actualiza la fecha de fin.
   */
  onEndDateChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.filterEndDate.set(input.value);
  }

  /**
   * Aplica los filtros de fecha explícitamente (al pulsar el botón Buscar).
   */
  applyDateFilters(): void {
    this.loadMovements();
    this.currentPage.set(1);
  }

  /**
   * Limpia todos los filtros y recarga el historial completo.
   */
  clearFilters(): void {
    this.filterType.set('');
    this.filterStartDate.set('');
    this.filterEndDate.set('');
    this.loadMovements();
    this.currentPage.set(1);
  }

  /**
   * Consume el servicio de productos para poblar el selector del formulario de nuevo movimiento.
   * * @returns {void}
   */
  loadProducts(): void {
    this.productService.getProducts().subscribe({
      next: (data) => {
        this.products.set(data.filter(p => p.is_active));
      },
      error: (err) => console.error('Error cargando productos para el select:', err)
    });
  }

  /**
   * Abre el modal para registrar un nuevo movimiento y resetea el formulario.
   * * @returns {void}
   */
  openModal(): void {
    this.movementForm.reset({ quantity: 1, movement_type: '' });
    this.isModalOpen.set(true);
  }

  /**
   * Cierra el modal de registro y limpia los estados temporales.
   * * @returns {void}
   */
  closeModal(): void {
    this.isModalOpen.set(false);
    this.movementForm.reset();
  }

  /**
   * Abre el modal para visualizar el motivo/notas detalladas de un movimiento.
   * * @param {string} notes - El texto de las notas a visualizar.
   * @returns {void}
   */
  openNotesModal(notes: string): void {
    this.currentNotesToView.set(notes);
    this.isNotesModalOpen.set(true);
  }

  /**
   * Cierra el modal de vista de notas y limpia el texto actual.
   * * @returns {void}
   */
  closeNotesModal(): void {
    this.isNotesModalOpen.set(false);
    setTimeout(() => this.currentNotesToView.set(null), 200);
  }

  /**
   * Incrementa en 1 la cantidad del movimiento en el formulario.
   * @returns {void}
   */
  incrementQuantity(): void {
    const current = this.movementForm.get('quantity')?.value || 1;
    this.movementForm.patchValue({ quantity: current + 1 });
  }

  /**
   * Decrementa en 1 la cantidad del movimiento en el formulario, 
   * asegurando que el valor mínimo siempre sea 1.
   * @returns {void}
   */
  decrementQuantity(): void {
    const current = this.movementForm.get('quantity')?.value || 1;
    if (current > 1) {
      this.movementForm.patchValue({ quantity: current - 1 });
    }
  }

  /**
   * Busca en caché el nombre de un producto dado su UUID. 
   * Útil para renderizar la tabla si el backend solo envía el product_id.
   * * @param {string} productId - El UUID del producto.
   * @returns {string} El nombre del producto o una cadena genérica si no se encuentra.
   */
  getProductName(productId: string): string {
    const product = this.products().find(p => p.id === productId);
    return product ? product.name : 'Producto Desconocido';
  }

  /**
   * Procesa la validación y el envío del formulario para crear un nuevo movimiento.
   * Al tener éxito, actualiza la lista localmente.
   * * @returns {void}
   */
  onSubmit(): void {
    if (this.movementForm.invalid) {
      this.movementForm.markAllAsTouched();
      return;
    }

    this.isSaving.set(true);
    const movementData = this.movementForm.value;

    this.movementService.createMovement(movementData).subscribe({
      next: (newMovement) => {
        this.movements.update(moves => [newMovement, ...moves]);
        toast.success(`Registro de ${newMovement.movement_type.toLowerCase()} exitoso.`);
        this.closeModal();
        this.isSaving.set(false);
      },
      error: (err) => {
        console.error('Error guardando movimiento:', err);

        let errorDetail = 'Verifica los datos e intenta de nuevo.';
        if (err.error?.detail) {
          errorDetail = typeof err.error.detail === 'string'
            ? err.error.detail
            : JSON.stringify(err.error.detail);
        }

        toast.error('Error al registrar');

        this.isSaving.set(false);
      }
    });
  }

  /**
   * Getter auxiliar para acceder a los controles del formulario en la vista HTML.
   */
  get f() { return this.movementForm.controls; }

  /**
   * Prepara los datos de movimientos actuales y los exporta a Excel.
   * @returns {void}
   */
  exportToExcel(): void {
    const movements = this.movements();
    if (movements.length === 0) return;

    const dataToExport = movements.map(mov => ({
      'ID': mov.id,
      'Fecha': new Date(mov.created_at).toLocaleDateString(),
      'Tipo': mov.movement_type,
      'Producto': mov.product?.name || 'N/A',
      'Cantidad': mov.quantity,
      'Motivo': mov.reason || 'Sin detalles'
    }));

    this.exportService.exportToExcel(dataToExport, 'Reporte_Movimientos');
  }

  /**
   * Prepara los datos de movimientos actuales y los exporta a PDF.
   * @returns {void}
   */
  exportToPdf(): void {
    const movements = this.movements();
    if (movements.length === 0) return;

    const headers = ['Fecha', 'Tipo', 'Producto', 'Cantidad', 'Motivo'];
    
    const dataToExport = movements.map(mov => [
      new Date(mov.created_at).toLocaleDateString(),
      mov.movement_type,
      mov.product?.name || 'N/A',
      mov.quantity.toString(),
      mov.reason || '-'
    ]);

    this.exportService.exportToPdf(headers, dataToExport, 'Reporte_Movimientos', 'Historial de Movimientos de Inventario');
  }
}