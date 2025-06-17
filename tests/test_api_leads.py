# tests/test_api_leads.py
from fastapi.testclient import TestClient
import random
import string

# Gera um e-mail único para cada execução do teste
def generate_unique_email():
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"lead.teste.{random_suffix}@exemplo.com"

def test_create_lead_success(client: TestClient):
    """Testa a criação de um novo lead com sucesso."""
    lead_data = { "nome": "Lead Válido", "email": generate_unique_email() }
    response = client.post("/leads/", json=lead_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == lead_data["email"]

def test_create_lead_duplicate_email(client: TestClient):
    """Testa a falha ao criar um lead com um e-mail duplicado."""
    email_unico = generate_unique_email()
    lead_data_1 = { "nome": "Primeiro Lead", "email": email_unico }
    lead_data_2 = { "nome": "Lead Duplicado", "email": email_unico }

    # Cria o primeiro lead com sucesso
    response1 = client.post("/leads/", json=lead_data_1)
    assert response1.status_code == 201

    # Tenta criar o segundo com o mesmo e-mail, esperando um erro 400
    response2 = client.post("/leads/", json=lead_data_2)
    assert response2.status_code == 400
    assert "E-mail já cadastrado" in response2.json()["detail"]

def test_read_all_leads_empty(client: TestClient):
    """Testa a leitura de todos os leads quando o banco está limpo."""
    response = client.get("/leads/")
    assert response.status_code == 200
    assert response.json() == []

def test_read_all_leads_with_data(client: TestClient):
    """Testa a leitura de leads após a criação."""
    lead_data = { "nome": "Lead para Leitura", "email": generate_unique_email() }
    client.post("/leads/", json=lead_data)

    response = client.get("/leads/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["email"] == lead_data["email"]