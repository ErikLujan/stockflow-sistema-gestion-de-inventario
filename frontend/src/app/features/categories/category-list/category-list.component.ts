import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CategoryService } from '../../../core/services/category.service';
import { Category } from '../../../shared/models/category.model';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-category-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './category-list.component.html'
})
export class CategoryListComponent implements OnInit {
  private categoryService = inject(CategoryService);
  private fb = inject(FormBuilder);

  // Estados de la lista
  categories = signal<Category[]>([]);
  isLoading = signal<boolean>(true);
  error = signal<string | null>(null);

  // Estados del Modal de Formulario
  isModalOpen = signal<boolean>(false);
  isSaving = signal<boolean>(false);
  isEditMode = signal<boolean>(false);
  selectedCategoryId = signal<string | null>(null);

  // Estados del Modal de Eliminación
  isDeleteModalOpen = signal<boolean>(false);
  categoryToDeleteId = signal<string | null>(null);

  categoryForm: FormGroup = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(100)]],
    description: ['', [Validators.maxLength(250)]]
  });

  // Estados de Paginación
  currentPage = signal<number>(1);
  itemsPerPage = signal<number>(5);

  // Señal computada: extrae solo las categorías de la página actual
  paginatedCategories = computed(() => {
    const start = (this.currentPage() - 1) * this.itemsPerPage();
    const end = start + this.itemsPerPage();
    return this.categories().slice(start, end);
  });

  // Señal computada: calcula el total de páginas
  totalPages = computed(() => {
    return Math.ceil(this.categories().length / this.itemsPerPage()) || 1;
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
   * Inicializa el componente y solicita la carga de la tabla de categorías.
   * * @returns {void}
   */
  ngOnInit(): void {
    this.loadCategories();
  }

  /**
   * Consume el servicio para obtener la lista de categorías y actualiza el estado.
   * * @returns {void}
   */
  loadCategories(): void {
    this.isLoading.set(true);
    this.error.set(null);
    this.categoryService.getCategories().subscribe({
      next: (data) => {
        this.categories.set(data);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Error:', err);
        this.error.set('No se pudieron cargar las categorías.');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Abre el modal del formulario. Si se pasa una categoría, se configura en modo edición.
   * * @param {Category} [category]
   * @returns {void}
   */
  openModal(category?: Category): void {
    this.categoryForm.reset();
    if (category) {
      this.isEditMode.set(true);
      this.selectedCategoryId.set(category.id);
      this.categoryForm.patchValue(category);
    } else {
      this.isEditMode.set(false);
      this.selectedCategoryId.set(null);
    }
    this.isModalOpen.set(true);
  }

  /**
   * Cierra el modal del formulario y limpia los estados temporales.
   * * @returns {void}
   */
  closeModal(): void {
    this.isModalOpen.set(false);
    this.selectedCategoryId.set(null);
    this.categoryForm.reset();
  }

  /**
   * Procesa la información del formulario para crear o actualizar una categoría.
   * * @returns {void}
   */
  onSubmit(): void {
    if (this.categoryForm.invalid) {
      this.categoryForm.markAllAsTouched();
      return;
    }

    this.isSaving.set(true);
    const categoryData = this.categoryForm.value;
    const currentId = this.selectedCategoryId();

    if (this.isEditMode() && currentId) {
      this.categoryService.updateCategory(currentId, categoryData).subscribe({
        next: (updatedCategory) => {
          this.categories.update(cats => cats.map(c => c.id === currentId ? updatedCategory : c));
          toast.success('Categoría actualizada con éxito');
          this.closeModal();
          this.isSaving.set(false);
        },
        error: (err) => this.handleError(err)
      });
    } else {
      this.categoryService.createCategory(categoryData).subscribe({
        next: (newCategory) => {
          this.categories.update(cats => [...cats, newCategory]);
          toast.success('Nueva categoría creada');
          this.closeModal();
          this.isSaving.set(false);
        },
        error: (err) => this.handleError(err)
      });
    }
  }

  /**
   * Abre el modal de confirmación para eliminar una categoría.
   * * @param {string} id - El UUID de la categoría a eliminar.
   * @returns {void}
   */
  openDeleteModal(id: string): void {
    this.categoryToDeleteId.set(id);
    this.isDeleteModalOpen.set(true);
  }

  /**
   * Cierra el modal de eliminación y limpia el ID seleccionado.
   * * @returns {void}
   */
  closeDeleteModal(): void {
    this.isDeleteModalOpen.set(false);
    this.categoryToDeleteId.set(null);
  }

  /**
   * Confirma y ejecuta la solicitud HTTP para eliminar la categoría seleccionada.
   * * @returns {void}
   */
  confirmDelete(): void {
    const id = this.categoryToDeleteId();
    if (!id) return;

    this.categoryService.deleteCategory(id).subscribe({
      next: () => {
        this.categories.update(cats => cats.filter(c => c.id !== id));
        toast.success('Categoría eliminada');
        this.closeDeleteModal();
      },
      error: (err) => {
        console.error('Error eliminando:', err);
        toast.error('Error al intentar eliminar la categoría');
        this.closeDeleteModal();
      }
    });
  }

  /**
   * Maneja los errores HTTP al intentar guardar información.
   * * @private
   * @param {any} err
   * @returns {void}
   */
  private handleError(err: any): void {
    console.error('Error guardando categoría:', err);
    toast.error('Error al procesar la solicitud', {
      description: err.error?.detail || 'Revisa los datos ingresados e intenta de nuevo.'
    });
    this.isSaving.set(false);
  }

  /**
   * Getter auxiliar para acceder a los controles del formulario desde el template HTML.
   */
  get f() { return this.categoryForm.controls; }
}