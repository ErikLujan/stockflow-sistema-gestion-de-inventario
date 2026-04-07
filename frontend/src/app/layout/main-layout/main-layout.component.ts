import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router, NavigationEnd } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { toast } from 'ngx-sonner';
import { filter } from 'rxjs';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './main-layout.component.html'
})
export class MainLayoutComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  isSidebarOpen: boolean = false;
  isAdmin = signal<boolean>(false);

  isProfileMenuOpen = signal<boolean>(false);
  userEmail = signal<string>('Usuario');

  animatePage = signal<boolean>(true);

  constructor() {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.animatePage.set(false);
      setTimeout(() => this.animatePage.set(true), 10);
    });
  }

  ngOnInit() {
    const userRole = this.authService.getUserRole();
    this.isAdmin.set(userRole?.toLowerCase() === 'admin');

    const email = this.authService.getUserEmail();
    if (email) {
      this.userEmail.set(email);
    }
  }

  /**
   * Alterna el estado de visibilidad de la barra lateral.
   * Se utiliza en el botón de menú tipo hamburguesa en pantallas pequeñas.
   * * @returns {void}
   */
  toggleSidebar(): void {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  /**
   * Cierra explícitamente la barra lateral.
   * Es útil al hacer clic en un enlace de navegación para que el menú se oculte automáticamente en móviles.
   * * @returns {void}
   */
  closeSidebar(): void {
    this.isSidebarOpen = false;
  }

  /**
     * Alterna el estado de visibilidad del menú flotante del perfil de usuario.
     * * @returns {void}
     */
  toggleProfileMenu(): void {
    this.isProfileMenuOpen.update(v => !v);
  }

  /**
   * Cierra explícitamente el menú flotante del perfil de usuario.
   * Se utiliza al hacer clic fuera del menú para mejorar la experiencia de usuario.
   * * @returns {void}
   */
  closeProfileMenu(): void {
    this.isProfileMenuOpen.set(false);
  }

  /**
   * Ejecuta el proceso de cierre de sesión.
   * Destruye la sesión en el servicio de autenticación, redirige al usuario a la pantalla de login 
   * y muestra una notificación visual de éxito.
   * * @returns {void}
   */
  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
    toast.success('¡Sesión cerrada con éxito!');
  }
}