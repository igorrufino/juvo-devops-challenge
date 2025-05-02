# app/providers/factory.py
from .base import ScoreProvider
from .mock_provider import MockScoreProvider
import os

async def get_score_provider() -> ScoreProvider:
    """
    Factory para obter o provedor de score apropriado
    com base na configuração do ambiente
    """
    provider_type = os.getenv("SCORE_PROVIDER", "mock")
    
    if provider_type == "serasa" and os.getenv("SERASA_API_KEY"):
        from .serasa_provider import SerasaProvider
        return SerasaProvider(
            api_key=os.getenv("SERASA_API_KEY"),
            api_url=os.getenv("SERASA_API_URL")
        )
    elif provider_type == "spc" and os.getenv("SPC_API_KEY"):
        from .spc_provider import SPCProvider
        return SPCProvider(
            api_key=os.getenv("SPC_API_KEY"),
            api_url=os.getenv("SPC_API_URL")
        )
    elif provider_type == "bacen" and os.getenv("BACEN_API_KEY"):
        from .bacen_provider import BacenProvider
        return BacenProvider(
            api_key=os.getenv("BACEN_API_KEY"),
            api_url=os.getenv("BACEN_API_URL") 
        )
    else:
        # Fallback para mock se nenhum outro provedor estiver configurado
        return MockScoreProvider()