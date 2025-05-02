<<<<<<< HEAD
# score-api
=======
score-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── services.py
│   └── utils/
│       ├── __init__.py
│       ├── cpf_validator.py
│       └── logging_config.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_cpf_validator.py
├── Dockerfile
├── requirements.txt
└── README.md

# Passo a Passo para Testar a API de Score

Vou detalhar como testar sua API de Score completa, incluindo as novas funcionalidades de processamento em lote e integração com provedores externos.

## 1. Configuração do Ambiente

```bash
# Ativar ambiente virtual se ainda não estiver
python3 -m venv venv
```


```bash
# Ativar o ambiente virtual
source venv/bin/activate

# Definir o PYTHONPATH
export PYTHONPATH=$PWD
```

## 2. Iniciar a API

```bash
# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. Testar Endpoint de Health Check

```bash
# Verificar status da API
curl -v http://localhost:8000/api/v1/health
```

Você deve ver uma resposta similar a:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-04-25T01:30:25.123456",
  "environment": "development",
  "services": {
    "postgres": "connected",
    "redis": "disconnected (using memory cache)",
    "score_provider": "configured (mock)"
  }
}
```

## 4. Testar CPF Individual

### 4.1. CPF Válido

```bash
curl -X POST http://score-api.score-api.com.br/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"cpf": "529.982.247-25"}'
```

```bash
curl -X GET http://score-api.score-api.com.br/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"cpf": "529.982.247-25"}'
```

Você deve receber um score válido:
```json
{
  "cpf": "52998224725",
  "score": 78,
  "category": "Bom",
  "timestamp": "2025-04-25T01:31:42.123456",
  "request_id": "abc123def456"
}
```

### 4.2. CPF Inválido

```bash
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"cpf": "111.111.111-11"}'
```

Você deve receber um erro 422:
```json
{
  "detail": [
    {
      "loc": ["body", "cpf"],
      "msg": "CPF inválido",
      "type": "value_error"
    }
  ]
}
```

## 5. Testar Processamento em Lote

```bash
curl -X POST http://localhost:8000/api/v1/score/batch \
  -H "Content-Type: application/json" \
  -d '["529.982.247-25", "787.156.939-67", "083.302.999-46"]'
```

Você deve receber múltiplos scores:
```json
[
  {
    "cpf": "52998224725",
    "score": 78,
    "category": "Bom",
    "timestamp": "2025-04-25T01:33:12.123456",
    "request_id": "abc123def456"
  },
  {
    "cpf": "78715693967",
    "score": 92,
    "category": "Excelente",
    "timestamp": "2025-04-25T01:33:12.234567",
    "request_id": "abc123def456"
  },
  {
    "cpf": "08330299946",
    "score": 45,
    "category": "Regular",
    "timestamp": "2025-04-25T01:33:12.345678",
    "request_id": "abc123def456"
  }
]
```

### 5.1. Testar Limite de Lote

Se configurou `MAX_BATCH_SIZE=5`, envie mais de 5 CPFs:

```bash
curl -X POST http://localhost:8000/api/v1/score/batch \
  -H "Content-Type: application/json" \
  -d '["111.222.333-44", "222.333.444-55", "333.444.555-66", "444.555.666-77", "555.666.777-88", "666.777.888-99"]'
```

Você deve receber um erro 400:
```json
{
  "detail": "Número máximo de CPFs por lote excedido. Limite: 5"
}
```

## 6. Testar Comportamento de Cache

Execute a mesma consulta duas vezes em sequência:

```bash
# Primeira consulta
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"cpf": "529.982.247-25"}'

# Segunda consulta (deve ser mais rápida e retornar exatamente o mesmo score)
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"cpf": "529.982.247-25"}'
```

Verifique nos logs que a segunda requisição foi atendida pelo cache.

## 7. Testar com Provedor Externo (Simulado)

```bash
# Configurar para usar provedor externo
export SCORE_PROVIDER="serasa"
export PROVIDER_API_KEY="chave-api-teste"
export PROVIDER_API_URL="http://exemplo.com/api"

# Reiniciar a API para aplicar configurações
# [Interrompa o servidor com Ctrl+C e execute novamente o comando uvicorn]

# Testar novamente
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"cpf": "529.982.247-25"}'
```

O log deve mostrar tentativa de buscar do provedor, mas como não há conexão real, usará o fallback local.

## 8. Testar Documentação Interativa

Abra no navegador:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 9. Monitoramento e Logs

Para testar o monitoramento, você pode observar os logs gerados. Eles devem conter informações detalhadas sobre cada requisição, incluindo:
- Tempo de processamento
- De onde o score foi obtido (cache, banco de dados, cálculo)
- Erros encontrados

```bash
# Ver os logs em tempo real
# Já deve estar visível no terminal onde você iniciou a API
```

## 10. Testes sob Carga

Para testar o comportamento sob carga, você pode usar ferramentas como `ab` (Apache Benchmark) ou `wrk`:

```bash
# Instalar ab 
sudo apt install apache2-utils

# Criar arquivo JSON para teste
echo '{"cpf": "529.982.247-25"}' > test.json

# Executar teste com 100 requisições, 10 concorrentes
ab -n 100 -c 10 -T 'application/json' -p test.json http://localhost:8000/api/v1/score
```

## 11. Testes Automatizados

Se quiser executar os testes unitários:

```bash
# Executar todos os testes
pytest -v

# Testar apenas o validador de CPF
pytest -v tests/test_cpf_validator.py

# Testar apenas a API
pytest -v tests/test_api.py
```

## 12. Testando com Redis e PostgreSQL (Opcional)

Se você quiser testar com os serviços reais:

```bash
# Instalar dependências adicionais
pip install psycopg2-binary redis

# Iniciar PostgreSQL e Redis (usando Docker)
docker run --name postgres-score -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=scoredb -p 5432:5432 -d postgres:14-alpine
docker run --name redis-score -p 6379:6379 -d redis:alpine

# Configurar variáveis de ambiente
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=scoredb
export REDIS_HOST=localhost
export REDIS_PORT=6379

# Reiniciar a API
# [Interrompa o servidor com Ctrl+C e execute novamente o comando uvicorn]

# Verificar status da API
curl http://localhost:8000/api/v1/health
```

A resposta deve mostrar conexões ativas com Redis e PostgreSQL.

## 13. Verificação Final

Para garantir que tudo está funcionando corretamente, faça uma sequência de testes:

1. Health check
2. Um CPF válido
3. Um CPF inválido
4. Um lote pequeno de CPFs
5. Verificação de cache (mesmo CPF várias vezes)

Com estes testes, você terá validado todas as principais funcionalidades da API.
>>>>>>> master
