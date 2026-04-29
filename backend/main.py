from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import generate, benchmark, evaluate, recommend, history

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Local AI Benchmark Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, tags=["Generate"])
app.include_router(benchmark.router, tags=["Benchmark"])
app.include_router(evaluate.router, tags=["Evaluate"])
app.include_router(recommend.router, tags=["Recommend"])
app.include_router(history.router, tags=["History"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Local AI Benchmark Dashboard API"}
