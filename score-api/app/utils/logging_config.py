# app/utils/logging_config.py
import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def configure_logging():
    """
    Configura o logging da aplicação.
    """
    # Configurações baseadas no ambiente
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    
    # Configuração básica
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    # Configurar logger raiz
    root_logger = logging.getLogger()
    
    # Limpar handlers existentes
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # Em produção, adicionamos um handler para arquivo
    if environment == "production":
        try:
            # Garantir que o diretório de logs existe
            log_dir = "/var/log/score-api"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Handler para arquivo com rotação
            file_handler = RotatingFileHandler(
                f"{log_dir}/score-api.log",
                maxBytes=10485760,  # 10MB
                backupCount=10
            )
            file_handler.setLevel(logging.INFO)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_format)
            root_logger.addHandler(file_handler)
        except Exception as e:
            # Se falhar ao configurar o handler de arquivo, logamos no console
            logging.error(f"Erro ao configurar log em arquivo: {str(e)}")