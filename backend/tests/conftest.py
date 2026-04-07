"""
Configuración global para las pruebas unitarias.
Define cómo nos conectamos a la base de datos y a la API durante los tests.
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.core.config import settings
from app.models.user import User

engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Crea una sesión limpia para cada test.
    Hace un ROLLBACK al terminar para no guardar datos basura en tu base de datos real.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Cliente HTTP de pruebas que intercepta la base de datos 
    para usar la sesión aislada (db_session).
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def auth_client(client):
    """
    Cliente HTTP que simula estar autenticado.
    Evita tener que hacer login en cada test aislando la prueba del endpoint.
    """
    fake_user = User(
        id=uuid.uuid4(), 
        email="test@inventario.com", 
        is_active=True
    )
    
    def override_get_current_user():
        return fake_user
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client

    app.dependency_overrides.pop(get_current_user, None)