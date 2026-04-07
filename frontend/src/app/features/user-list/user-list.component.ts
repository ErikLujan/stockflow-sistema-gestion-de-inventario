import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl } from '@angular/forms';
import { UserService } from '../../core/services/user.service';
import { User } from '../../shared/models/user.model';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './user-list.component.html',
  styleUrl: './user-list.component.scss'
})
export class UserListComponent implements OnInit {
  private userService = inject(UserService);
  private fb = inject(FormBuilder);

  // --- Estados de la Vista ---
  users = signal<User[]>([]);
  isLoading = signal<boolean>(true);
  error = signal<string | null>(null);

  // --- Estados de Modales ---
  isModalOpen = signal<boolean>(false);
  isDeleteModalOpen = signal<boolean>(false);
  isSaving = signal<boolean>(false);

  // --- Estados de Visibilidad de Contraseña ---
  showPassword = signal<boolean>(false);
  showConfirmPassword = signal<boolean>(false);
  
  selectedUser = signal<User | null>(null);

  userForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    confirmPassword: ['', [Validators.required]],
    role: ['user', [Validators.required]],
    is_active: [true]
  }, { validators: this.passwordMatchValidator });

  /**
   * Validador personalizado para comprobar que las contraseñas coincidan.
   */
  passwordMatchValidator(control: AbstractControl) {
    const password = control.get('password')?.value;
    const confirmPassword = control.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { mismatch: true };
  }

  /**
   * Inicializa el componente y carga la lista de usuarios.
   */
  ngOnInit(): void {
    this.loadUsers();
  }

  /**
   * Consume el servicio para obtener los usuarios.
   */
  loadUsers(): void {
    this.isLoading.set(true);
    this.error.set(null);
    this.userService.getUsers().subscribe({
      next: (data) => {
        this.users.set(data);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Error cargando usuarios:', err);
        this.error.set('No se pudo cargar la lista de usuarios.');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Abre el modal para crear un nuevo usuario.
   */
  openModal(): void {
    this.selectedUser.set(null);
    this.userForm.reset({ role: 'user', is_active: true });

    this.showPassword.set(false);
    this.showConfirmPassword.set(false);

    this.userForm.get('password')?.setValidators([Validators.required, Validators.minLength(8)]);
    this.userForm.get('confirmPassword')?.setValidators([Validators.required]);
    this.userForm.get('password')?.updateValueAndValidity();
    this.userForm.get('confirmPassword')?.updateValueAndValidity();

    this.isModalOpen.set(true);
  }

  togglePasswordVisibility(): void {
    this.showPassword.update(v => !v);
  }

  toggleConfirmPasswordVisibility(): void {
    this.showConfirmPassword.update(v => !v);
  }

  /**
   * Cierra el modal principal.
   */
  closeModal(): void {
    this.isModalOpen.set(false);
    this.userForm.reset();
  }

  /**
   * Getter auxiliar para el formulario.
   */
  get f() { return this.userForm.controls; }

  /**
   * Procesa el formulario para crear un usuario.
   */
  onSubmit(): void {
    if (this.userForm.invalid) {
      this.userForm.markAllAsTouched();
      return;
    }

    this.isSaving.set(true);
    const userData = this.userForm.value;
    delete userData.confirmPassword;

    this.userService.createUser(userData).subscribe({
      next: (newUser) => {
        this.users.update(users => [newUser, ...users]);
        toast.success('Usuario creado exitosamente.');
        this.closeModal();
        this.isSaving.set(false);
      },
      error: (err) => {
        console.error('Error guardando usuario:', err);
        const detail = err.error?.detail || 'Error al registrar el usuario.';
        toast.error(typeof detail === 'string' ? detail : 'Verifica los datos.');
        this.isSaving.set(false);
      }
    });
  }

  /**
   * Abre el modal de confirmación de eliminación.
   */
  deleteUser(user: User): void {
    this.selectedUser.set(user);
    this.isDeleteModalOpen.set(true);
  }

  /**
   * Cierra el modal de eliminación.
   */
  closeDeleteModal(): void {
    this.isDeleteModalOpen.set(false);
    this.selectedUser.set(null);
  }

  /**
   * Confirma y ejecuta la eliminación del usuario.
   */
  confirmDelete(): void {
    const user = this.selectedUser();
    if (!user) return;

    this.userService.deleteUser(user.id).subscribe({
      next: () => {
        this.users.update(users => users.filter(u => u.id !== user.id));
        toast.success('Usuario eliminado correctamente.');
        this.closeDeleteModal();
      },
      error: (err) => {
        console.error('Error eliminando usuario:', err);
        toast.error('No se pudo eliminar al usuario.');
        this.closeDeleteModal();
      }
    });
  }
}
