# Projeto de Infraestrutura e DevOps

Este repositório contém uma implementação completa de infraestrutura como código (IaC) usando Terraform, pipelines CI/CD com GitHub Actions, e componentes de monitoramento em um cluster Kubernetes na AWS.

## 📋 Visão Geral

Este projeto implementa uma infraestrutura completa que inclui:

- Criação de VPC, subnets e recursos de rede na AWS via Terraform
- Cluster EKS provisionado com Terraform
- Pipeline CI/CD usando GitHub Actions
- Implementação de uma API de Score de Crédito em Python/FastAPI
- Stack de monitoramento com Prometheus, Grafana, Loki e Tempo
- Configuração de service mesh com Istio

## 🏗️ Estrutura do Projeto

```
.
├── .github/workflows      # Pipelines CI/CD do GitHub Actions
├── docs                   # Documentação detalhada
├── infraestrutura         # Código Terraform para AWS
│   ├── eks                # Configuração do cluster EKS
│   └── s3                 # Configuração de bucket S3 para backend
├── kubernetes             # Manifestos Kubernetes
│   ├── deployment         # Deployments da aplicação
│   ├── monitoring         # Stack de monitoramento
│   ├── namespaces         # Definição de namespaces
│   └── networking         # Configuração de rede e Istio
└── score-api              # Código da API de exemplo
    ├── app/               # Código da aplicação
    │   ├── __init__.py
    │   ├── main.py
    │   ├── models.py
    │   ├── routes.py
    │   ├── services.py
    │   └── utils/
    ├── tests/             # Testes da aplicação
    │   ├── test_api.py
    │   └── test_cpf_validator.py
    ├── Dockerfile         # Configuração do container
    └── requirements.txt   # Dependências Python
```

## 🚀 Início Rápido

### Pré-requisitos

- Conta AWS com permissões adequadas
- AWS CLI configurado
- Terraform instalado (v1.0+)
- kubectl instalado
- Docker instalado

### Configuração Inicial

Para configurar o projeto, siga os passos da [documentação de requisitos](docs/1_-_doc_requisitos.md).

### Deploy da Infraestrutura

O deploy da infraestrutura acontece automaticamente através dos workflows do GitHub Actions quando há alterações no código do Terraform. Para mais detalhes, consulte a [documentação de Terraform](docs/5_-_doc_terraform_create.md).

### Deploy da Aplicação

A aplicação é construída e implantada automaticamente no cluster EKS quando há alterações no código da API. Para mais detalhes, consulte a [documentação de pipeline](docs/7_-_doc_pipeline.md).

## 📚 Documentação

Documentação detalhada está disponível na pasta `docs`:

- [0 - Inicialização do Projeto](docs/0_-_doc_init.md)
- [1 - Requisitos e Configuração](docs/1_-_doc_requisitos.md)
- [2 - Criação do Dockerfile](docs/2_-_doc_dockerfile_create.md)
- [3 - Testes Locais do Dockerfile](docs/3_-_doc_dockerfile_testes_locais.md)
- [4 - Deploy do ArgoCD](docs/4_-_doc_argocd_deploy.md)
- [5 - Criação do Terraform](docs/5_-_doc_terraform_create.md)
- [6 - Testes Locais do Terraform](docs/6_-_doc_terraform_testes_locais.md)
- [7 - Pipeline CI/CD](docs/7_-_doc_pipeline.md)
- [8 - Monitoramento](docs/8_-_doc_monitoring.md)
- [9 - Comandos Úteis](docs/9_-_comandos.md)

## 🔍 Sobre a API de Score

### Funcionalidades da API

A API Score fornece serviços para:
- Validação e processamento de CPF
- Cálculo de score de crédito individual
- Processamento em lote de múltiplos CPFs
- Caching de resultados para melhor performance
- Integração com provedores externos (configurável)

### Tecnologias Utilizadas

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL / SQLite
- **Cache**: Redis / Memory Cache
- **Containerização**: Docker
- **Documentação**: Swagger / ReDoc

### Docker e Containerização

A aplicação utiliza um Dockerfile otimizado para ambientes de produção:

```dockerfile
FROM python:3.10-slim

# Variáveis de ambiente padrão (não sensíveis)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=production

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema de uma vez (reduz o número de camadas e melhora o cache)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar o arquivo requirements.txt primeiro para otimizar o cache do Docker
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p /var/log/score-api && chmod 755 /var/log/score-api

# Criar usuário não-root
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app /var/log/score-api

# Definir o usuário não-root para o container
USER appuser

# Porta que será exposta (definida no Kubernetes)
EXPOSE 8000

# Health check (opcional, o Kubernetes pode fazer isso também)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
```

### Testando a API

#### Testes Locais

```bash
# Health Check
curl -v http://localhost:8000/api/v1/health

# Verificar score (CPF válido)
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"cpf": "529.982.247-25"}'

# Processamento em lote
curl -X POST http://localhost:8000/api/v1/score/batch \
  -H "Content-Type: application/json" \
  -d '["529.982.247-25", "787.156.939-67", "083.302.999-46"]'
```

#### Testes em Produção

```bash
# Health Check
curl -v https://score-api.score-api.com.br/api/v1/health

# Verificar score
curl -X POST https://score-api.score-api.com.br/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"cpf": "529.982.247-25"}'
```

Para testes mais detalhados, consulte a [documentação de testes](docs/3_-_doc_dockerfile_testes_locais.md) e [comandos úteis](docs/9_-_comandos.md).

## 🛠️ Implementações Técnicas

### Infraestrutura AWS

O projeto utiliza módulos Terraform para criar:

- VPC com subnets públicas e privadas
- Cluster EKS com node groups gerenciados
- Storage Class (gp3) para volumes persistentes
- IAM Roles e políticas necessárias

### Pipeline CI/CD

O projeto implementa diversos workflows do GitHub Actions:
- Aplicação do Terraform para criação de infraestrutura
- Instalação do Istio para service mesh
- Deploy de namespaces e recursos de rede
- Build e deploy da aplicação score-api

### Monitoramento

A stack de monitoramento inclui:
- Prometheus para coleta de métricas
- Grafana para visualização
- Loki para logs
- Tempo para tracing
- MinIO para armazenamento

## 🤔 Decisões Técnicas e Considerações

### Escolha de Tecnologias

- **GitHub Actions**
- **Terraform**
- **EKS**
- **Python/FastAPI**

### Melhorias Futuras

- Implementação de segurança adicional (AWS KMS, Vault)
- Adição de análise de código com SonarQube
- Implementação de varredura de vulnerabilidades com Trivy
- Melhoria na gestão de versões da aplicação
- Implementação do Keda para escalablidade da aplicação
- Implementação de dashboard específico para logs
- Adição de certificados autoassinados e DNS

## 📝 Notas do Autor

Este projeto representou um desafio significativo, especialmente pela adoção do Terraform e GitHub Actions, áreas em que busquei expandir minha experiência além da zona de conforto. Reconheço que há pontos a melhorar e planejo continuar aprimorando esta implementação com o tempo.

Para detalhes completos sobre as decisões técnicas e desafios enfrentados, consulte a [Documentação de Inicialização](docs/0_-_doc_init.md).

