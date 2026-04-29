import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./benchmark.db")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Scoring weights
WEIGHT_QUALITY = 0.4
WEIGHT_SPEED = 0.3
WEIGHT_MEMORY = 0.3
