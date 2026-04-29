# Local AI Model Benchmark Dashboard

A full-stack application to run, compare, and evaluate multiple local LLMs running via Ollama. It benchmarks models based on speed (tokens/sec), memory usage, and provides an objective ranking.

## Features
- **Parallel Model Execution**: Run multiple local LLMs simultaneously for a given prompt using `asyncio.gather`.
- **Metrics Tracking**: Accurately measures tokens per second, latency, and RAM usage.
- **Recommendation Engine**: Suggests the optimal model based on available RAM and your optimization preference (speed, quality, balanced).
- **History & Caching**: SQLite-backed caching ensures repeated prompts skip execution. Historical runs are visualized on a Recharts dashboard.

## Prerequisites
1. Install [Ollama](https://ollama.com/)
2. Install Python 3.9+
3. Install Node.js 18+

## Setup Instructions

### 1. Ollama & Models
Ensure Ollama is running (`ollama serve`). Pull the models you wish to benchmark:
```bash
ollama pull llama3
ollama pull mistral
ollama pull phi3
```

### 2. Backend Setup
Navigate to the `backend` directory, create a virtual environment, and run the server:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
uvicorn main:app --reload
```
The FastAPI backend will start at `http://localhost:8000`.

### 3. Frontend Setup
Navigate to the `frontend` directory, install dependencies, and run Vite:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser to access the dashboard.

## Methodology

### Benchmarking
Metrics like `tokens/sec` are extracted directly from Ollama's `eval_duration` and `eval_count` for precision. Memory tracking takes a snapshot of the process RSS before and after the prompt execution.

### Recommendation & Scoring
The system uses a transparent composite formula to rank models:
`score = (0.4 * normalized_quality) + (0.3 * normalized_speed) + (0.3 * normalized_memory_efficiency)`
- **Quality**: Blended score from an LLM-as-a-judge (via `instructor`) and standard heuristics.
- **Speed**: Derived from `tokens_per_sec`.
- **Memory Efficiency**: Inversely proportional to RAM consumed during execution.
