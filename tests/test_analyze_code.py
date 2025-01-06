from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_analyze_code():
    # Dados de exemplo para o teste
    code_snippet = "print('Hello, World!')"
    payload = {"code_snippet": code_snippet}

    # Enviar requisição POST para o endpoint
    response = client.post("/analyze-code", json=payload)

    # Verificar resposta
    assert response.status_code == 200
    response_data = response.json()
    assert "id" in response_data
    assert "suggestions" in response_data
    assert isinstance(response_data["suggestions"], list)
