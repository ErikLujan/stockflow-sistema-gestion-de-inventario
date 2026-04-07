import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html'
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  loginForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

  errorMessage = signal<string | null>(null);
  isLoading = signal<boolean>(false);
  showPassword = signal<boolean>(false);

  /**
   * Getter para acceder fácilmente a los controles del formulario desde el HTML.
   */
  get f() {
    return this.loginForm.controls;
  }

  /**
   * Alterna la visibilidad de la contraseña en el campo de entrada.
   * * @returns {void}
   */
  togglePassword(): void {
    this.showPassword.update(value => !value);
  }

  /**
   * Método que se ejecuta al enviar el formulario.
   * Valida los datos localmente y luego llama al servicio de autenticación.
   * * @returns {void}
   */
  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.errorMessage.set(null);
    this.isLoading.set(true);

    const loginData = this.loginForm.value;

    this.authService.login(loginData).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.router.navigate(['/dashboard']);   
        toast.success('¡Sesión iniciada con éxito!');
      },
      error: (err) => {
        this.isLoading.set(false);
        if (err.status === 401 || err.status === 400) {
          this.errorMessage.set('Credenciales incorrectas. Inténtalo de nuevo.');
        } else {
          this.errorMessage.set('Ocurrió un error en el servidor. Inténtalo más tarde.');
        }
        console.error('Login error:', err);
      }
    });
  }
}