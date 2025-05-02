# app/providers/mock_provider.py
from .base import ScoreProvider
import random

class MockScoreProvider(ScoreProvider):
    """Provedor simulado para desenvolvimento local"""
    
    async def get_score(self, cpf: str) -> dict:
        # Lógica atual de cálculo 
        cpf_sum = sum(int(digit) for digit in cpf if digit.isdigit())
        cpf_product = 1
        for digit in cpf:
            if digit.isdigit() and int(digit) > 0:
                cpf_product *= int(digit)
        
        seed = (cpf_sum * 17 + cpf_product) % 100
        random.seed(seed)
        score_value = random.randint(0, 100)
        
        # Categorizar o score
        if score_value >= 80:
            category = "Excelente"
        elif score_value >= 60:
            category = "Bom"
        elif score_value >= 40:
            category = "Regular"
        else:
            category = "Ruim"
            
        return {
            "score": score_value,
            "category": category,
            "source": "mock"
        }

# app/providers/serasa_provider.py (exemplo de implementação futura)
from .base import ScoreProvider
import aiohttp

class SerasaProvider(ScoreProvider):
    """Provedor que consulta a API da Serasa"""
    
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
    
    async def get_score(self, cpf: str) -> dict:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            async with session.post(
                f"{self.api_url}/score",
                json={"cpf": cpf},
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Mapear resposta da Serasa para o formato interno
                    score_value = data.get("score", 0)
                    
                    # Categorizar o score conforme regras da Serasa
                    if score_value >= 700:
                        category = "Excelente"
                    elif score_value >= 500:
                        category = "Bom"
                    elif score_value >= 300:
                        category = "Regular"
                    else:
                        category = "Ruim"
                        
                    return {
                        "score": score_value,
                        "category": category,
                        "source": "serasa",
                        "raw_data": data
                    }
                else:
                    # Fallback para provider local em caso de falha
                    return await MockScoreProvider().get_score(cpf)