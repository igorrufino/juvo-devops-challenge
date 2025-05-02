from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks, Body, Query
from .services import calculate_score, get_latest_score_record, get_cache
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import ScoreRequest, ScoreResponse, HealthResponse, BatchScoreRequest, ScoreBatchResponse
from .services import calculate_score, get_latest_score_record
from .utils.cpf_validator import validate_cpf
from .database.config import get_db, redis_client, USE_REDIS
from datetime import datetime
import logging
import time
import uuid
import os
import asyncio

# Configuração de logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Configurações via variáveis de ambiente
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "1000"))
CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", "100"))

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
        
        # Calcular score (indicando que não é parte de um lote)
        score_response = await calculate_score(cpf, db, request_id, is_batch=False)
        
        # Log de métricas para monitoramento
        process_time = time.time() - start_time
        logger.info(f"Request {request_id}: Tempo de processamento: {process_time:.4f}s")
        
        # Adicionar tarefa em background para análise
        background_tasks.add_task(log_request_metrics, request_id, cpf[-4:] if len(cpf) >= 4 else cpf, process_time)
            
        return score_response
    
    except Exception as e:
        logger.error(f"Request {request_id}: Erro interno: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno ao processar a solicitação. Por favor, tente novamente."
        )

@router.post("/score/batch", response_model=List[ScoreBatchResponse], tags=["score"])
async def batch_score(
    cpfs: List[str] = Body(..., example=["123.456.789-09", "987.654.321-00"]),
    db: Session = Depends(get_db),
    request_id: str = Depends(add_request_id)
):
    """
    Processa múltiplos CPFs em uma única chamada.
    Limite configurável via variável de ambiente MAX_BATCH_SIZE.
    Retorna informações sobre todos os CPFs, incluindo os inválidos.
    """
    try:
        # Verificar se está dentro do limite de tamanho
        if len(cpfs) > MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"Número máximo de CPFs por lote excedido. Limite: {MAX_BATCH_SIZE}"
            )
        
        start_time = time.time()
        logger.info(f"Request {request_id}: Recebida solicitação em lote com {len(cpfs)} CPFs")
        
        # Processar CPFs de forma assíncrona com limite de concorrência
        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
        cpf_results = []  # Lista para armazenar resultados e informações
        
        async def process_with_limit(cpf):
            async with semaphore:
                try:
                    # Remover caracteres não numéricos
                    clean_cpf = ''.join(filter(str.isdigit, cpf))
                    
                    # Formatar CPF para exibição nos logs
                    if len(clean_cpf) >= 11:
                        formatted_cpf = f"{clean_cpf[0:3]}.{clean_cpf[3:6]}.{clean_cpf[6:9]}-{clean_cpf[9:11]}"
                    else:
                        formatted_cpf = cpf
                    
                    # Verificar se tem 11 dígitos
                    if len(clean_cpf) != 11:
                        cpf_results.append({"cpf": formatted_cpf, "valid": False, "reason": "não tem 11 dígitos"})
                        return None
                        
                    # Verificar dígitos repetidos
                    if clean_cpf == clean_cpf[0] * 11:
                        cpf_results.append({"cpf": formatted_cpf, "valid": False, "reason": "dígitos repetidos"})
                        return None
                    
                    # Verificar manualmente
                    # Cálculo do primeiro dígito verificador
                    soma = 0
                    for i in range(9):
                        soma += int(clean_cpf[i]) * (10 - i)
                    resto = soma % 11
                    digito1 = 0 if resto < 2 else 11 - resto
                    
                    # Verificação do primeiro dígito
                    if digito1 != int(clean_cpf[9]):
                        cpf_results.append({"cpf": formatted_cpf, "valid": False, "reason": "dígito verificador 1 inválido"})
                        return None
                    
                    # Cálculo do segundo dígito verificador
                    soma = 0
                    for i in range(10):
                        soma += int(clean_cpf[i]) * (11 - i)
                    resto = soma % 11
                    digito2 = 0 if resto < 2 else 11 - resto
                    
                    # Verificação do segundo dígito
                    if digito2 != int(clean_cpf[10]):
                        cpf_results.append({"cpf": formatted_cpf, "valid": False, "reason": "dígito verificador 2 inválido"})
                        return None
                    
                    # Se chegou aqui, o CPF é válido
                    score_response = await calculate_score(clean_cpf, db, request_id, is_batch=True)
                    
                    # Armazenar resultado completo
                    cpf_results.append({
                        "cpf": formatted_cpf, 
                        "valid": True, 
                        "score": score_response.score,
                        "category": score_response.category,
                        "response": score_response
                    })
                    
                    return score_response
                except Exception as e:
                    cpf_results.append({"cpf": cpf, "valid": False, "reason": f"erro: {str(e)}"})
                    return None
        
        # Criar tasks para todos os CPFs
        tasks = [process_with_limit(cpf) for cpf in cpfs]
        results = await asyncio.gather(*tasks)
        
        # Filtrar resultados None (CPFs inválidos)
        valid_results = [result for result in results if result is not None]
        
        # Preparar resposta com todos os CPFs (válidos e inválidos)
        batch_responses = []
        
        for result_info in cpf_results:
            if result_info["valid"]:
                # CPF válido
                response = ScoreBatchResponse(
                    cpf=result_info["cpf"],
                    status="valid",
                    score=result_info["score"],
                    category=result_info["category"],
                    timestamp=result_info["response"].timestamp,
                    request_id=request_id
                )
                # Log para CPF válido
                logger.info(
                    f"Request {request_id}: CPF válido '{result_info['cpf']}' - "
                    f"Score: {result_info['score']}, Categoria: {result_info['category']}"
                )
            else:
                # CPF inválido
                response = ScoreBatchResponse(
                    cpf=result_info["cpf"],
                    status="invalid",
                    reason=result_info["reason"]
                )
                # Log para CPF inválido
                logger.warning(
                    f"Request {request_id}: CPF inválido '{result_info['cpf']}' - "
                    f"Motivo: {result_info['reason']}"
                )
            
            batch_responses.append(response)
        
        # Log de métricas para monitoramento
        process_time = time.time() - start_time
        logger.info(f"Request {request_id}: Processados {len(valid_results)}/{len(cpfs)} CPFs em {process_time:.4f}s")
        
        return batch_responses
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request {request_id}: Erro interno: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno ao processar o lote. Por favor, tente novamente."
        )

@router.get("/score/{cpf}", response_model=ScoreResponse, tags=["score"])
async def get_score_by_cpf(
    cpf: str,
    db: Session = Depends(get_db),
    request_id: str = Depends(add_request_id)
):
    """
    Obtém o score mais recente para um CPF específico.
    Se o CPF nunca foi processado ou é inválido, retorna 404.
    """
    try:
        # Remover caracteres não numéricos do CPF
        clean_cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verificar se o CPF é válido
        if not validate_cpf(clean_cpf):
            raise HTTPException(
                status_code=400,
                detail=f"CPF inválido: {cpf}"
            )
        
        # Buscar no banco de dados
        db_record = get_latest_score_record(db, clean_cpf)
        
        if not db_record:
            # Se não encontrar no banco, verificar logs para debug
            logger.warning(f"Request {request_id}: CPF {clean_cpf} não encontrado no banco de dados")
            
            # Podemos decidir buscar no cache como fallback, mas por enquanto retornamos 404
            raise HTTPException(
                status_code=404,
                detail=f"CPF não encontrado: {cpf}"
            )
        
        # Construir resposta
        response = ScoreResponse(
            cpf=clean_cpf,
            score=db_record.score,
            category=db_record.category,
            timestamp=db_record.created_at,
            request_id=request_id
        )
        
        # Log da consulta
        logger.info(f"Request {request_id}: Consulta de score para CPF: {cpf[-4:] if len(cpf) >= 4 else cpf}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request {request_id}: Erro ao consultar CPF {cpf}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar a consulta."
        )
# Função para logs de métricas em background
async def log_request_metrics(request_id: str, cpf_suffix: str, process_time: float):
    """Função executada em background para métricas e análise"""
    # Em um ambiente real, aqui enviaríamos métricas para um sistema como Prometheus/Grafana
    logger.info(f"Métricas - Request: {request_id}, CPF: {cpf_suffix}, Tempo: {process_time:.4f}s")