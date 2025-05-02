# app/utils/cpf_validator.py

import logging

# Configuração de logging
logger = logging.getLogger(__name__)

def validate_cpf(cpf: str) -> bool:
    """
    Valida um CPF utilizando o algoritmo oficial.
    
    Args:
        cpf: String contendo o CPF (pode conter pontos e hífen)
        
    Returns:
        bool: True se o CPF é válido, False caso contrário
    """
    # Verificar se o CPF é None ou não é string
    if cpf is None or not isinstance(cpf, str):
        logger.debug("CPF é None ou não é string")
        return False
        
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se o CPF tem 11 dígitos
    if len(cpf) != 11:
        logger.debug(f"CPF {cpf} não tem 11 dígitos")
        return False
    
    # Verifica se todos os dígitos são iguais (caso inválido)
    if cpf == cpf[0] * 11:
        logger.debug(f"CPF {cpf} tem todos os dígitos iguais")
        return False
    
    try:
        # Cálculo do primeiro dígito verificador
        soma = 0
        for i in range(9):
            soma += int(cpf[i]) * (10 - i)
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Verificação do primeiro dígito
        if digito1 != int(cpf[9]):
            logger.debug(f"CPF {cpf} com primeiro dígito verificador inválido")
            return False
        
        # Cálculo do segundo dígito verificador
        soma = 0
        for i in range(10):
            soma += int(cpf[i]) * (11 - i)
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verificação do segundo dígito
        if digito2 != int(cpf[10]):
            logger.debug(f"CPF {cpf} com segundo dígito verificador inválido")
            return False
        
        logger.debug(f"CPF {cpf} é válido")
        return True
    except Exception as e:
        # Em caso de erro no cálculo (por exemplo, caracteres não numéricos)
        logger.error(f"Erro ao validar CPF {cpf}: {str(e)}")
        return False