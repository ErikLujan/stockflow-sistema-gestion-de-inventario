"""
Pruebas unitarias para los endpoints de Categorías.
"""
from fastapi import status

def test_create_category_success(auth_client):
    """
    Verifica que un usuario autenticado pueda crear una categoría válida.
    """
    payload = {
        "name": "Categoría de Prueba",
        "description": "Descripción para el test unitario"
    }
    
    response = auth_client.post("/api/v1/categories/", json=payload)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert "id" in data
    assert data["is_active"] is True

def test_create_category_duplicate_name(auth_client):
    """
    Verifica que el sistema rechace la creación de una categoría si el nombre ya existe.
    """
    payload = {"name": "Categoría Única"}
    
    auth_client.post("/api/v1/categories/", json=payload)
    
    response = auth_client.post("/api/v1/categories/", json=payload)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "ya existe" in response.json()["detail"].lower()

def test_get_categories(auth_client):
    """
    Verifica que el endpoint de lectura devuelva una lista de categorías.
    """
    auth_client.post("/api/v1/categories/", json={"name": "Categoría Listado"})
    
    response = auth_client.get("/api/v1/categories/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_soft_delete_category(auth_client):
    """
    Verifica que al eliminar una categoría, esta devuelva un 204 y ya no aparezca en la lista.
    """
    create_res = auth_client.post("/api/v1/categories/", json={"name": "Categoría a Borrar"})
    category_id = create_res.json()["id"]
    
    delete_res = auth_client.delete(f"/api/v1/categories/{category_id}")
    assert delete_res.status_code == status.HTTP_204_NO_CONTENT
    
    get_res = auth_client.get("/api/v1/categories/")
    categories = get_res.json()

    assert not any(c["id"] == category_id for c in categories)