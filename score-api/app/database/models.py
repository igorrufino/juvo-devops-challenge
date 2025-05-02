# app/database/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from .config import Base

class ScoreRecord(Base):
    __tablename__ = "score_records"
    
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(11), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    category = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Índices para otimização de consultas
    __table_args__ = (
        Index('idx_cpf_created', cpf, created_at.desc()),
    )