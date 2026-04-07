"""
Módulo de inyección de dependencias para la base de datos.
"""
from typing import Generator
from app.core.database import SessionLocal

def get_db() -> Generator:
    """
    Proporciona una sesión de base de datos aislada para cada petición (request).
    El bloque try/finally garantiza que la conexión se devuelva al pool
    incluso si ocurre una excepción durante la petición.
    
    Yields:
        Session: Instancia de sesión de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()