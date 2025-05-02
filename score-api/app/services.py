from .models import ScoreRequest, ScoreResponse
from .database.config import redis_client, USE_REDIS, get_db
from .database.models import ScoreRecord
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import uuid
import random
import time
import json
import os

# Configuração de logging
logger = logging.getLogger(__name__)

# Cache em memória para fallback caso o Redis não esteja disponível
memory_cache = {}

def get_cache_key(cpf: str) -> str:
    """Gera uma chave para o cache"""
    return f"score:{cpf}"

def set_cache(cpf: str, score_data: dict, ttl: int = 3600):
    """
    Armazena no cache (Redis ou memória)
    
    Args:
        cpf: CPF do cliente
        score_data: Dados do score para cache
        ttl: Tempo de vida em segundos (padrão: 1 hora)
    """
    cache_key = get_cache_key(cpf)
    
    if USE_REDIS:
        try:
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(score_data)
            )
            logger.debug(f"Score para CPF {cpf[-4:]} armazenado no Redis")
        except Exception as e:
            logger.error(f"Erro ao armazenar no Redis: {str(e)}")
            # Fallback para cache em memória
            memory_cache[cache_key] = {
                'data': score_data,
                'expires_at': time.time() + ttl
            }
    else:
        # Cache em memória
        memory_cache[cache_key] = {
            'data': score_data,
            'expires_at': time.time() + ttl
        }
        logger.debug(f"Score para CPF {cpf[-4:]} armazenado no cache em memória")
        
        # Limpeza de cache expirado (caso cache em memória cresça muito)
        if len(memory_cache) > 10000:
            current_time = time.time()
            keys_to_delete = [
                k for k, v in memory_cache.items() 
                if v['expires_at'] < current_time
            ]
            for key in keys_to_delete:
                del memory_cache[key]

def get_cache(cpf: str) -> dict:
    """
    Recupera dados do cache (Redis ou memória)
    
    Args:
        cpf: CPF do cliente
        
    Returns:
        dict: Dados do score ou None se não estiver em cache
    """
    cache_key = get_cache_key(cpf)
    
    if USE_REDIS:
        try:
            data = redis_client.get(cache_key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Erro ao consultar Redis: {str(e)}")
            # Tentar fallback para cache em memória
            if cache_key in memory_cache:
                cache_item = memory_cache[cache_key]
                if cache_item['expires_at'] > time.time():
                    return cache_item['data']
    else:
        # Cache em memória
        if cache_key in memory_cache:
            cache_item = memory_cache[cache_key]
            if cache_item['expires_at'] > time.time():
                return cache_item['data']
    
    return None

def store_score_record(db: Session, cpf: str, score: int, category: str):
    """
    Armazena o registro de score no banco de dados
    
    Args:
        db: Sessão do banco de dados
        cpf: CPF do cliente
        score: Valor do score
        category: Categoria do score
    """
    try:
        # Criar novo registro
        score_record = ScoreRecord(
            cpf=cpf,
            score=score,
            category=category
        )
        
        # Adicionar à sessão e commit
        db.add(score_record)
        db.commit()
        
        # Log silencioso para evitar duplicação com o log final
        logger.debug(f"Score para CPF {cpf[-4:]} armazenado no banco de dados")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao armazenar score no banco de dados: {str(e)}")
        return False

def get_latest_score_record(db: Session, cpf: str):
    """
    Recupera o score mais recente do banco de dados
    
    Args:
        db: Sessão do banco de dados
        cpf: CPF do cliente
        
    Returns:
        ScoreRecord: Registro mais recente ou None
    """
    try:
        return db.query(ScoreRecord)\
            .filter(ScoreRecord.cpf == cpf)\
            .order_by(ScoreRecord.created_at.desc())\
            .first()
    except Exception as e:
        logger.error(f"Erro ao consultar banco de dados: {str(e)}")
        return None

async def calculate_score(cpf: str, db: Session, request_id: str = None, is_batch: bool = False) -> ScoreResponse:
    """
    Calcula ou recupera o score de crédito com base no CPF.
    
    Args:
        cpf: CPF do cliente (já validado)
        db: Sessão do banco de dados
        request_id: ID opcional da requisição para rastreamento
        is_batch: Indica se é parte de um processamento em lote
        
    Returns:
        ScoreResponse: Objeto contendo o score calculado
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    # Log de início do processamento (nível debug para reduzir verbosidade)
    logger.debug(f"Request {request_id}: Processando score para CPF: {cpf[-4:]} (final)")
    
    # Formatar CPF para exibição
    if len(cpf) >= 11:
        formatted_cpf = f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
    else:
        formatted_cpf = cpf
    
    # 1. Verificar cache primeiro
    cached_data = get_cache(cpf)
    if cached_data:
        logger.debug(f"Request {request_id}: Score encontrado em cache para CPF: {cpf[-4:]}")
        
        response = ScoreResponse(
            cpf=cpf,
            score=cached_data['score'],
            category=cached_data['category'],
            timestamp=datetime.fromisoformat(cached_data['timestamp']),
            request_id=request_id
        )
        
        # Se não for parte de um lote, log do resultado
        if not is_batch:
            logger.info(f"Request {request_id}: CPF válido '{formatted_cpf}' - Score: {cached_data['score']}, Categoria: {cached_data['category']}")
        
        return response
    
    # 2. Se não estiver em cache, verificar banco de dados
    db_record = get_latest_score_record(db, cpf)
    if db_record:
        # Verificar se o registro é recente (menos de 1 dia)
        age = (datetime.now() - db_record.created_at).total_seconds()
        if age < 86400:  # 24 horas em segundos
            logger.debug(f"Request {request_id}: Score encontrado no banco para CPF: {cpf[-4:]}")
            
            # Converter para resposta
            response = ScoreResponse(
                cpf=cpf,
                score=db_record.score,
                category=db_record.category,
                timestamp=db_record.created_at,
                request_id=request_id
            )
            
            # Armazenar em cache para futuras consultas
            set_cache(cpf, {
                'score': db_record.score,
                'category': db_record.category,
                'timestamp': db_record.created_at.isoformat()
            })
            
            # Se não for parte de um lote, log do resultado
            if not is_batch:
                logger.info(f"Request {request_id}: CPF válido '{formatted_cpf}' - Score: {db_record.score}, Categoria: {db_record.category}")
            
            return response
    
    # 3. Se não estiver no banco ou for antigo, calcular novo score
    try:
        logger.debug(f"Request {request_id}: Calculando novo score para CPF: {cpf[-4:]}")
        
        # Simulação de latência de serviço externo (em um ambiente real)
        time.sleep(0.1)
        
        # Em um ambiente real, aqui chamaríamos um serviço/modelo ML para calcular o score
        # Para este exemplo, vamos gerar um score "determinístico" baseado no CPF
        cpf_sum = sum(int(digit) for digit in cpf if digit.isdigit())
        cpf_product = 1
        for digit in cpf:
            if digit.isdigit() and int(digit) > 0:
                cpf_product *= int(digit)
        
        # Criar um número determinístico mas que pareça aleatório baseado no CPF
        seed = (cpf_sum * 17 + cpf_product) % 100
        random.seed(seed)
        score_value = random.randint(0, 100)
        
        # Definir categoria com base no score
        if score_value >= 80:
            category = "Excelente"
        elif score_value >= 60:
            category = "Bom"
        elif score_value >= 40:
            category = "Regular"
        else:
            category = "Ruim"
        
        # Salvar no banco de dados
        now = datetime.now()
        store_score_record(db, cpf, score_value, category)
        
        # Criar resposta
        response = ScoreResponse(
            cpf=cpf,
            score=score_value,
            category=category,
            timestamp=now,
            request_id=request_id
        )
        
        # Salvar no cache
        set_cache(cpf, {
            'score': score_value,
            'category': category,
            'timestamp': now.isoformat()
        })
        
        # Log do resultado - apenas se não for parte de um lote
        if not is_batch:
            logger.info(f"Request {request_id}: CPF válido '{formatted_cpf}' - Score: {score_value}, Categoria: {category}")
        
        return response
        
    except Exception as e:
        logger.error(f"Request {request_id}: Erro ao calcular score: {str(e)}")
        raise