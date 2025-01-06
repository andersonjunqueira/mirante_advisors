# Prerequisitos

- Pyton 3.13
- Docker
- Esse passo a passo é para execução no Windows.

# Preparação

## PostgreSQL

Executando uma instância do PostgreSQL:
```
docker run --name postgres-container -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 -d postgres
```

Iniciando o prompt do PostgreSQL:
```
docker exec -it postgres-container psql -U postgres
```

Criando o usuário e banco de dados:
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

Executar a aplicação:
```
uvicorn app.main:app --reload
```

Para testar o endpoint /analyze_code:

PowerShell (Windows)
```
$code_snippet = "print('Hello, World!')"
$payload = @{ code_snippet = $code_snippet } | ConvertTo-Json -Depth 1
$response = Invoke-RestMethod -Uri http://localhost:8000/analyze-code -Method POST -Body $payload -ContentType "application/json"
$response
```

# Testes Unitários

Para executar os testes unitários:
```
pytest
```

Iniciando o prompt do PostgreSQL:
```
docker exec -it postgres-container psql -U advisors_user -d advisors_db
```

Verificando as análises gravadas bo banco:
```
SELECT * FROM analysis_history;
```

# Observações

* A tabela no banco de dados será criada automaticamente contando que o banco esteja rodando e o usuário padrão do banco seja postgres / yourpassword

* O projeto inclui informações sensíveis 'hardcoded' nos arquivos como senha do usuário do banco apenas por ser um desafio técnico e não uma aplicação real. Essas informações devem ser guardadas de forma mais segura (um exemplo seria usar o recurso de secrets do kubernetes ao rodar esse agente em um container)

* Os testes unitários incluídos com esse projeto devem ser considerados como testes de integração uma vez que os testes unitários deveriam simular o acesso a recursos da infraestrutura como banco de dados.

# Item 3 - Integração com CrewAI

A análise do código é feita por uma função no arquivo app/services.py, no entando, a idéia seria integrar com a plataforma Crew AI o que poderia ser feito através de uma biblioteca python chamada crewai.

* Definir os agentes e tarefas do Crew AI:
```
from crewai import Agent, Task, Crew, Process

def create_crew():
    """
    Define os agentes e tarefas para análise de código Python.
    """

    # Agente 1: Identificador de problemas de código
    linter_agent = Agent(
        role='Linter',
        goal='Identificar problemas e violações de boas práticas em código Python.',
        verbose=True,
        memory=False,
        backstory='Especialista em encontrar problemas no código e sugerir correções.'
    )

    # Agente 2: Gerador de melhorias de código
    optimizer_agent = Agent(
        role='Otimizador',
        goal='Fornecer melhorias de desempenho e legibilidade no código Python.',
        verbose=True,
        memory=False,
        backstory='Um agente com vasta experiência em refatoração de código Python.'
    )

    # Tarefa 1: Analisar o código
    lint_task = Task(
        description="Analise o código fornecido e liste os problemas detectados.",
        expected_output="Uma lista detalhada de problemas no código.",
        agent=linter_agent
    )

    # Tarefa 2: Sugerir melhorias
    optimize_task = Task(
        description="Com base nos problemas detectados, sugira melhorias claras e acionáveis.",
        expected_output="Uma lista de sugestões para melhorar o código.",
        agent=optimizer_agent
    )

    # Definir o Crew (workflow sequencial)
    crew = Crew(
        agents=[linter_agent, optimizer_agent],
        tasks=[lint_task, optimize_task],
        process=Process.sequential,  # Executa as tarefas uma após a outra
    )

    return crew

def kickoff_crew(code_snippet: str):
    """
    Executa o workflow do CrewAI para análise de código.

    Args:
        code_snippet (str): O código Python a ser analisado.

    Returns:
        dict: Resultado da análise.
    """
    crew = create_crew()
    inputs = {"code_snippet": code_snippet}
    return crew.kickoff(inputs=inputs)
```

* Trocar a chamada do arquivo services.py por algo semelhante:
```
from crews.crew_manager import kickoff_crew
...
result = kickoff_crew(code.code_snippet)
return {"result": result}
```

Veja que eu não testei essa integração, essa sessão é baseada em pesquisas que fiz na internet.

# Item 4 - Arquitetura e Escalabilidade

Recentemente eu preparei uma arquitetura em python para um projeto com múltiplos passos usando kubernetes e filas de mensagens que acredito que seria uma boa opção para escalar a idéia desse desafio.

Utilizar uma fila de mensagens é uma boa idéia para manter uma organização dos trechos de códigos que estão chegando.
Poderíamos usar cache, mas, prefiro a segurança das filas persistentes do RabbitMQ ou do AWS SQS.
Poderíamos usar uma tabela de banco de dados, mas, teríamos que lidar com locks e um certo custo de performance mas as filas de mensagens e já tem tudo isso pronto.

A aplicação poderia ser empacotada em uma imagem docker e executada dentro do kubernetes. Vantagens?
* Aumentar ou diminuir o número de processos em execução seria simples com o kubernetes. Podemos configurar métricas da fila e aumentar o numero de pods rodando se a fila tiver muitas mensagens ou diminuir se tiver poucas. 
* Cada agente 'escutaria' uma fila específica, receberia e processaria as mensagens uma por uma gravando o seu resultado no banco de dados.
* A UI consultaria no banco quais tarefas foram concluídas e disponibilizaria os resultados.
* Atualizar um agente seria simples como fazer o push de uma imagem docker.
* Criar novos agentes seria da mesma forma simples apenas fazendo o deploy no kubernetes sem necessidade de interromper os agentes de outras tarefas já em execução.