"""
Módulo que define los esquemas Pydantic para la autenticación.
"""
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    """
    Esquema para recibir las credenciales de inicio de sesión desde el cliente en formato JSON.
    """
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """
    Esquema para devolver el token de acceso al cliente.
    El refresh token no se incluye aquí porque viaja en una cookie de forma independiente.
    """
    access_token: str
    token_type: str = "bearer"