# app/database/config.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
import logging

logger = logging.getLogger(__name__)

# Configurações do PostgreSQL
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "scoredb")

# URL de conexão com fallback para SQLite em memória
try:
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(DATABASE_URL)
    # Testar conexão
    with engine.connect() as conn:
        pass
    logger.info("Conectado ao PostgreSQL com sucesso")
except Exception as e:
    logger.warning(f"Não foi possível conectar ao PostgreSQL: {str(e)}")
    logger.warning("Usando SQLite em memória como fallback")
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Configuração do Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = os.getenv("REDIS_DB", "0")

# Cliente Redis com fallback para dicionário em memória
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=int(REDIS_PORT),
        password=REDIS_PASSWORD,
        db=int(REDIS_DB),
        socket_timeout=5,
        decode_responses=True
    )
    # Testar conexão
    redis_client.ping()
    logger.info("Conectado ao Redis com sucesso")
    USE_REDIS = True
except Exception as e:
    logger.warning(f"Não foi possível conectar ao Redis: {str(e)}")
    logger.warning("Usando cache em memória como fallback")
    USE_REDIS = False
    # O fallback será um dicionário em memória implementado no service

# Configuração da sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Função para obter uma sessão de banco de dados.
    Usado como dependência nas rotas.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()