# app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import time
import uvicorn
import os
from .routes import router
from .utils.logging_config import configure_logging
from .database.init_db import init_db
from .metrics import init_metrics, MetricsMiddleware


# Configurar logging
configure_logging()
logger = logging.getLogger(__name__)

# Obter ambiente
environment = os.getenv("ENVIRONMENT", "development")

# Definir configurações com base no ambiente
if environment == "production":
    debug = False
    # Em produção, só permitiríamos domínios específicos
    allowed_origins = [
        "https://app.example.com",
        "https://api.example.com"
    ]
else:
    debug = True
    # Em desenvolvimento, permitimos origens mais amplas
    allowed_origins = ["*"]

app = FastAPI(
    title="API de Score de Crédito",
    description="API para consulta de score de crédito por CPF",
    version="1.0.0",
    debug=debug
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware)

# Middleware de compressão para reduzir tráfego de rede
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Extrair informações da requisição
    request_id = request.headers.get("X-Request-ID", "unspecified")
    start_time = time.time()
    
    # Log de início da requisição
    logger.info(f"Request {request_id}: {request.method} {request.url.path}")
    
    # Processar requisição
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Adicionar headers com informações de performance
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        # Log de conclusão
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"completed in {process_time:.4f}s with status {response.status_code}"
        )
        
        return response
    except Exception as e:
        # Log de erro
        process_time = time.time() - start_time
        logger.error(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"failed after {process_time:.4f}s with error: {str(e)}"
        )
        raise

# Adicionar rotas
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info(f"API iniciando no ambiente {environment}...")
    # Inicializar banco de dados
    init_db()
    init_metrics(port=8001)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API encerrando...")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # No desenvolvimento, habilitamos o reload para facilitar
    reload = environment != "production"
    
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)