# app/models.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.utils.cpf_validator import validate_cpf
from typing import List, Optional, Union, Any

class ScoreRequest(BaseModel):
    cpf: str = Field(..., description="CPF do cliente")
    
    @validator('cpf')
    def cpf_must_be_valid(cls, v):
        """Valida o CPF usando o algoritmo oficial"""
        if not validate_cpf(v):
            raise ValueError('CPF inválido')
        return v

class ScoreResponse(BaseModel):
    cpf: str
    score: int
    category: str
    timestamp: datetime
    request_id: str

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    environment: str
    services: dict = {}

class BatchScoreRequest(BaseModel):
    cpfs: List[str]

class ScoreBatchResponse(BaseModel):
    cpf: str
    status: str  # "valid" ou "invalid"
    score: Optional[int] = None
    category: Optional[str] = None
    reason: Optional[str] = None  # Motivo de rejeição para CPFs inválidos
    timestamp: Optional[datetime] = None
    request_id: Optional[str] = None