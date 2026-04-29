from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, index=True)
    model_name = Column(String, index=True)
    quantization = Column(String, index=True)
    
    # Metrics
    latency_ms = Column(Float)
    tokens_generated = Column(Integer)
    tokens_per_sec = Column(Float)
    ram_usage_mb = Column(Float)
    
    # Evaluation
    quality_score = Column(Float, nullable=True) # Normalized 0-10
    speed_score = Column(Float, nullable=True) # Normalized 0-10
    memory_score = Column(Float, nullable=True) # Normalized 0-10
    total_score = Column(Float, nullable=True)
    
    response_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CacheEntry(Base):
    __tablename__ = "cache_entries"

    id = Column(Integer, primary_key=True, index=True)
    prompt_hash = Column(String, unique=True, index=True)
    response_text = Column(Text)
    latency_ms = Column(Float)
    tokens_generated = Column(Integer)
    tokens_per_sec = Column(Float)
