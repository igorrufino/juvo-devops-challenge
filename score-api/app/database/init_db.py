# app/database/init_db.py
from .config import engine, Base
import logging

logger = logging.getLogger(__name__)

def init_db():
    """
    Inicializa o banco de dados criando as tabelas necessárias.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        raise