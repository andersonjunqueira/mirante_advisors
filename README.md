# Prerequisitos

- Pyton 3.13
- Docker

# Preparação

## PostgreSQL

Executando uma instância do PostgreSQL:
```
docker run --name postgres-container -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 -d postgres
```

Criando o banco de dados:
```
docker exec -it postgres-container psql -U postgres
```

No postgres prompt:
```
CREATE ROLE advisors_user WITH LOGIN PASSWORD 'advisorspassword';
CREATE DATABASE advisors_db OWNER advisors_user;
GRANT ALL PRIVILEGES ON DATABASE advisors_db TO advisors_user;
GRANT CONNECT ON DATABASE advisors_db TO advisors_user;
exit
```

Testando o novo usuário do banco:
```
docker exec -it postgres-container psql -U advisors_user -d advisors_db
``` 

## Python

Crie um runtime do python para esse projeto:
```
python -m venv venv
```

Ative o ambiente de desenvolvimento e instale os prerequisitos:
```
venv\Scripts\activate.bat
pip install -r requirements.txt
```

# Execução
uvicorn app.main:app --reload

Para testar o endpoint /analyze_code:

PowerShell (Windows)
```
$code_snippet = "print('Hello, World!')"
$payload = @{ code_snippet = $code_snippet } | ConvertTo-Json -Depth 1
$response = Invoke-RestMethod -Uri http://localhost:8000/analyze-code -Method POST -Body $payload -ContentType "application/json"
$response
```

curl (Linux)
```
curl -X POST http://localhost:8000/analyze-code ^
-H "Content-Type: application/json" ^
-d "{\"code_snippet\": \"print('Hello, World!')\"}"
```

# Testes Unitários

Para executar os testes unitários:
```
pytest
```