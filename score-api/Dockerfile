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

# Copiar o arquivo requirements.txt primeiro para otimizar o cache do Docker.
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
