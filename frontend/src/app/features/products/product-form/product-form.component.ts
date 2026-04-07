import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ProductService } from '../../../core/services/product.service';
import { CategoryService } from '../../../core/services/category.service';
import { Category } from '../../../shared/models/category.model';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-product-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './product-form.component.html'
})
export class ProductFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private productService = inject(ProductService);
  private categoryService = inject(CategoryService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  isLoading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  isEditMode = signal<boolean>(false);
  productId: string | null = null;

  categories = signal<Category[]>([]);
  isDropdownOpen = signal<boolean>(false);

  // Lista estática de unidades permitidas en el sistema
  readonly validUnits = ['unidades', 'kg', 'litros', 'cajas', 'metros', 'pares', 'gramos'];

  productForm: FormGroup = this.fb.group({
    sku: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
    name: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(150)]],
    unit_of_measure: ['', [Validators.required, Validators.maxLength(20)]],
    category_id: ['', [Validators.required]],
    min_stock: [10, [Validators.min(0)]],
    supplier: ['', [Validators.maxLength(150)]],
    notes: ['']
  });

  /**
   * Inicializa el componente.
   * Carga la lista de categorías y, si detecta un ID en la URL, 
   * configura el formulario en modo edición y obtiene los datos del producto.
   * * @returns {void}
   */
  ngOnInit(): void {
    this.loadCategories();

    this.productId = this.route.snapshot.paramMap.get('id');
    if (this.productId) {
      this.isEditMode.set(true);
      this.productForm.get('sku')?.disable();
      this.loadProductData(this.productId);
    }
  }

  /**
   * Obtiene la lista de categorías activas desde el backend.
   * * @returns {void}
   */
  loadCategories(): void {
    this.categoryService.getCategories().subscribe({
      next: (data) => this.categories.set(data),
      error: (err) => {
        console.error('Error cargando categorías:', err);
        toast.error('No se pudieron cargar las categorías');
      }
    });
  }

  /**
   * Obtiene los datos de un producto específico y los carga en el formulario reactivo.
   * * @param {string} id - El UUID del producto a editar.
   * @returns {void}
   */
  loadProductData(id: string): void {
    this.isLoading.set(true);
    this.productService.getProductById(id).subscribe({
      next: (product) => {
        this.productForm.patchValue(product);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Error cargando producto:', err);
        this.errorMessage.set('No se pudo cargar la información del producto.');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Alterna el estado de visibilidad del menú desplegable de categorías.
   * * @returns {void}
   */
  toggleDropdown(): void {
    this.isDropdownOpen.update(val => !val);
  }

  /**
   * Asigna la categoría seleccionada al control del formulario y cierra el menú.
   * * @param {string} categoryId - El UUID de la categoría seleccionada.
   * @returns {void}
   */
  selectCategory(categoryId: string): void {
    this.productForm.patchValue({ category_id: categoryId });
    this.isDropdownOpen.set(false);
  }

  /**
   * Busca y retorna el nombre de la categoría seleccionada actualmente.
   * * @returns {string} El nombre de la categoría o una cadena vacía si no hay selección.
   */
  getSelectedCategoryName(): string {
    const selectedId = this.productForm.get('category_id')?.value;
    const category = this.categories().find(c => c.id === selectedId);
    return category ? category.name : '';
  }

  /**
   * Incrementa en 1 el valor del control de stock mínimo.
   * * @returns {void}
   */
  incrementMinStock(): void {
    const current = this.productForm.get('min_stock')?.value || 0;
    this.productForm.patchValue({ min_stock: current + 1 });
  }

  /**
   * Decrementa en 1 el valor del control de stock mínimo, evitando números negativos.
   * * @returns {void}
   */
  decrementMinStock(): void {
    const current = this.productForm.get('min_stock')?.value || 0;
    if (current > 0) {
      this.productForm.patchValue({ min_stock: current - 1 });
    }
  }

  /**
   * Procesa el envío del formulario. 
   * Valida los datos y decide si ejecutar la creación o la actualización del registro.
   * * @returns {void}
   */
  onSubmit(): void {
    if (this.productForm.invalid) {
      this.productForm.markAllAsTouched();
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);
    const productData = this.productForm.value;

    if (this.isEditMode() && this.productId) {
      this.productService.updateProduct(this.productId, productData).subscribe({
        next: () => this.successRedirect(),
        error: (err) => this.handleError(err)
      });
    } else {
      this.productService.createProduct(productData).subscribe({
        next: () => this.successRedirect(),
        error: (err) => this.handleError(err)
      });
    }
  }

  /**
   * Maneja el flujo de éxito tras guardar un producto.
   * Detiene el estado de carga, muestra una notificación y redirige a la lista.
   * * @private
   * @returns {void}
   */
  private successRedirect(): void {
    this.isLoading.set(false);
    if (this.isEditMode()) {
      toast.success('Cambios guardados correctamente');
    } else {
      toast.success('Nuevo producto agregado con éxito');
    }
    this.router.navigate(['/productos']);
  }

  /**
   * Maneja el flujo de error tras un intento fallido de guardar un producto.
   * * @private
   * @param {any} err - El objeto de error retornado por la petición HTTP.
   * @returns {void}
   */
  private handleError(err: any): void {
    this.isLoading.set(false);

    const detail = err.error?.detail;

    if (typeof detail === 'string' && detail.toLowerCase().includes('sku')) {
      toast.error('Código SKU Duplicado', {
        description: 'Ya existe un producto registrado con este código. Por favor, ingresa un SKU diferente.'
      });
      this.errorMessage.set('El SKU ingresado ya está en uso.');
      return;
    }

    const backendError = detail ? (typeof detail === 'string' ? detail : JSON.stringify(detail)) : 'Verifica los datos.';
    toast.error('Hubo un error al guardar', {
      description: typeof detail === 'string' ? detail : 'Por favor, verifica los campos e intenta nuevamente.'
    });
    this.errorMessage.set(`Detalle: ${backendError}`);
  }
  /**
   * Getter auxiliar para acceder fácilmente a los controles del formulario en el HTML.
   */
  get f() { return this.productForm.controls; }
}