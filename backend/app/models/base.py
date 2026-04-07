"""
Módulo que define la clase base declarativa para los modelos ORM.
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Clase base de la cual heredarán todos los modelos ORM.
    Utiliza la sintaxis moderna de SQLAlchemy 2.0.
    """
    pass