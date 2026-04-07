import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ProductService } from '../../../core/services/product.service';
import { ExportService } from '../../../core/services/export.service';
import { Product } from '../../../shared/models/product.model';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './product-list.component.html'
})
export class ProductListComponent implements OnInit {
  private productService = inject(ProductService);
  private exportService = inject(ExportService);

  // Estados principales
  products = signal<Product[]>([]);
  isLoading = signal<boolean>(true);
  error = signal<string | null>(null);

  // Estado de busqueda
  searchTerm = signal<string>('');

  // Estados de Modales
  isModalOpen = signal<boolean>(false);
  isDetailModalOpen = signal<boolean>(false);
  selectedProduct = signal<Product | null>(null);

  isDeleteModalOpen = signal<boolean>(false);
  productToDeleteId = signal<string | null>(null);

  // Estados de Paginación
  currentPage = signal<number>(1);
  itemsPerPage = signal<number>(8);

  // Señal calculada que filtra la lista de productos en tiempo real.
  filteredProducts = computed(() => {
    const term = this.searchTerm().toLowerCase().trim();
    const currentProducts = this.products();

    if (!term) return currentProducts;

    return currentProducts.filter(p => 
      p.name.toLowerCase().includes(term) ||
      p.sku.toLowerCase().includes(term) ||
      (p.category_name && p.category_name.toLowerCase().includes(term))
    );
  });

  // Señal computada: extrae solo los productos de la página actual
  paginatedProducts = computed(() => {
    const start = (this.currentPage() - 1) * this.itemsPerPage();
    const end = start + this.itemsPerPage();
    return this.filteredProducts().slice(start, end);
  });

  // Señal computada: calcula el total de páginas
  totalPages = computed(() => {
    return Math.ceil(this.filteredProducts().length / this.itemsPerPage()) || 1;
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
   * Inicializa el componente y dispara la carga inicial de productos.
   * * @returns {void}
   */
  ngOnInit(): void {
    this.loadProducts();
  }

  /**
   * Obtiene la lista completa de productos desde el backend.
   * Maneja el estado de carga y posibles errores de red.
   * * @returns {void}
   */
  loadProducts(): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.productService.getProducts().subscribe({
      next: (data) => {
        this.products.set(data);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Error cargando productos:', err);
        this.error.set('No se pudieron cargar los productos. Intenta nuevamente.');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Actualiza el término de búsqueda al escribir en el input.
   * * @param {Event} event - Evento del input de texto.
   */
  onSearch(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.searchTerm.set(input.value);
    this.currentPage.set(1);
  }

  /**
   * Abre el modal para crear o editar un producto.
   * * @returns {void}
   */
  openModal(): void {
    this.isModalOpen.set(true);
  }

  /**
   * Cierra el modal de creación/edición de productos.
   * * @returns {void}
   */
  closeModal(): void {
    this.isModalOpen.set(false);
  }

  /**
   * Abre el modal de detalles y carga el producto seleccionado.
   * * @param {Product} product - El producto que se desea visualizar.
   * @returns {void}
   */
  viewProductDetail(product: Product): void {
    this.selectedProduct.set(product);
    this.isDetailModalOpen.set(true);
  }

  /**
   * Cierra el modal de detalles del producto y limpia la selección.
   * * @returns {void}
   */
  closeDetailModal(): void {
    this.isDetailModalOpen.set(false);
    this.selectedProduct.set(null);
  }

  /**
   * Abre el modal de confirmación para eliminar un producto.
   * * @param {string} id - El identificador único del producto a eliminar.
   * @returns {void}
   */
  deleteProduct(id: string): void {
    this.productToDeleteId.set(id);
    this.isDeleteModalOpen.set(true);
  }

  /**
   * Cierra el modal de confirmación de eliminación y limpia el ID temporal.
   * * @returns {void}
   */
  closeDeleteModal(): void {
    this.isDeleteModalOpen.set(false);
    this.productToDeleteId.set(null);
  }

  /**
   * Confirma y ejecuta la eliminación del producto seleccionado en el backend.
   * Actualiza la lista local de forma reactiva si la operación es exitosa.
   * * @returns {void}
   */
  confirmDelete(): void {
    const id = this.productToDeleteId();
    if (!id) return;

    this.productService.deleteProduct(id).subscribe({
      next: () => {
        this.products.update(currentProducts => currentProducts.filter(p => p.id !== id));
        this.closeDeleteModal();
        toast.success('Producto eliminado del catálogo');
      },
      error: (err) => {
        console.error('Error al eliminar:', err);
        this.closeDeleteModal();
        toast.error('No se pudo eliminar el producto');
      }
    });
  }

  /**
   * Exporta el catálogo actual de productos a un archivo Excel (.xlsx).
   * Mapea los datos para hacerlos amigables para el usuario final.
   * * @returns {void}
   */
  exportToExcel(): void {
    const prods = this.filteredProducts();
    if (prods.length === 0) return;

    const dataToExport = prods.map(p => ({
      'ID': p.id,
      'Nombre': p.name,
      'Categoría': p.category_name || 'Sin categoría',
      'Stock Actual': p.current_stock,
      'Stock Mínimo': p.min_stock,
      'Estado': p.is_active ? 'Activo' : 'Inactivo'
    }));

    this.exportService.exportToExcel(dataToExport, 'Reporte_Inventario_Actual');
  }

  /**
   * Exporta el catálogo actual de productos a un archivo PDF.
   * Genera una tabla estructurada con las columnas más relevantes.
   * * @returns {void}
   */
  exportToPdf(): void {
    const prods = this.filteredProducts();
    if (prods.length === 0) return;

    const headers = ['Nombre', 'Categoría', 'Stock', 'Mínimo', 'Estado'];
    
    const dataToExport = prods.map(p => [
      p.name,
      p.category_name|| '-',
      p.current_stock.toString(),
      p.min_stock.toString(),
      p.is_active ? 'Activo' : 'Inactivo'
    ]);

    this.exportService.exportToPdf(
      headers, 
      dataToExport, 
      'Reporte_Inventario_Actual', 
      'Estado Actual del Inventario'
    );
  }
}