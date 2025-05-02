# app/routes.py
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..models import ScoreRequest, ScoreResponse, HealthResponse
from ..services import calculate_score
from ..utils.cpf_validator import validate_cpf
from ..database.config import get_db, redis_client, USE_REDIS
from datetime import datetime
import logging
import time
import uuid
import os

# Configuração de logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Middleware para adicionar request_id
async def add_request_id(request: Request):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    return request_id

@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    """
    Endpoint de health check para verificar se a API está funcionando.
    Importante para monitoramento e liveness probes em Kubernetes.
    """
    # Verificar status dos serviços
    postgres_status = "connected"
    redis_status = "connected" if USE_REDIS else "disconnected (using memory cache)"
    
    try:
        # Tentar ping no Redis se estiver ativo
        if USE_REDIS:
            redis_client.ping()
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(),
        environment=os.getenv("ENVIRONMENT", "development"),
        services={
            "postgres": postgres_status,
            "redis": redis_status
        }
    )

@router.post("/score", response_model=ScoreResponse, tags=["score"])
async def get_score(
    request: ScoreRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    request_id: str = Depends(add_request_id)
):
    """
    Calcula e retorna o score de crédito com base no CPF.
    """
    try:
        start_time = time.time()
        logger.info(f"Request {request_id}: Recebida solicitação de score para CPF: {request.cpf[-4:] if len(request.cpf) >= 4 else request.cpf} (final)")
        
        # Remover caracteres não numéricos do CPF
        cpf = ''.join(filter(str.isdigit, request.cpf))
        
        # A validação já ocorreu via Pydantic, mas vamos registrar no log
        logger.info(f"Request {request_id}: CPF validado: {cpf[-4:] if len(cpf) >= 4 else cpf} (final)")
            
        # Calcular score
        score_response = calculate_score(cpf, db, request_id)
        
        # Log de métricas para monitoramento
        process_time = time.time() - start_time
        logger.info(f"Request {request_id}: Tempo de processamento: {process_time:.4f}s")
        
        # Adicionar tarefa em background para análise (exemplo)
        background_tasks.add_task(log_request_metrics, request_id, cpf[-4:] if len(cpf) >= 4 else cpf, process_time)
            
        return score_response
    
    except Exception as e:
        logger.error(f"Request {request_id}: Erro interno: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno ao processar a solicitação. Por favor, tente novamente."
        )

# Função para logs de métricas em background
async def log_request_metrics(request_id: str, cpf_suffix: str, process_time: float):
    """Função executada em background para métricas e análise"""
    # Em um ambiente real, aqui enviaríamos métricas para um sistema como Prometheus/Grafana
    logger.info(f"Métricas - Request: {request_id}, CPF: {cpf_suffix}, Tempo: {process_time:.4f}s")