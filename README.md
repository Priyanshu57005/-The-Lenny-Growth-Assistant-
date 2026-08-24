# The Lenny Growth Assistant

A full-stack, AI-powered conversational application grounded strictly in **Lenny's Podcast** and newsletter transcript knowledge. Built as a forward-deployed engineering application featuring RAG vector retrieval, multi-provider LLM support (Ollama local + Anthropic/OpenAI cloud), structured agent routing, a dedicated "Ship 30 for 30" essay generation skill, side-by-side secure HTML/Markdown artifact rendering, PostgreSQL session persistence, and containerized Docker setup.

---

## Key Features

- 🧠 **Transcript-Grounded RAG**: Precise answers cited directly to guests (Shreyas Doshi, Elena Verna, Brian Chesky, Casey Winters, Gibson Biddle) and episode timestamps.
- 🚫 **Anti-Hallucination Boundaries**: Explicitly acknowledges when available transcript data does not support an answer.
- ⚡ **Multi-Provider LLM Abstraction**: Seamlessly switch between local **Ollama** (`llama3.2`), **Anthropic Claude** (`claude-3-5-sonnet`), and **OpenAI** (`gpt-4o-mini`).
- ✍️ **Ship 30 for 30 Skill**: Dedicated agent tool for generating ~1,250-word structured, highly actionable growth essays.
- 🎨 **Artifact Canvas**: Side-by-side Claude-style Artifact Viewer rendering Markdown documents and sandboxed HTML/CSS components.
- 🛡️ **HTML Sandbox Security**: Enforces Content Security Policy (CSP) and `iframe` isolation (`sandbox="allow-scripts"` without `allow-same-origin`) to prevent XSS.
- 💬 **Isolated Session Persistence**: Conversation histories persisted in PostgreSQL with zero cross-session context leaks.

---

## Quick Start (Docker - Recommended)

```bash
# 1. Clone repository
git clone https://github.com/your-username/lenny-growth-assistant.git
cd lenny-growth-assistant

# 2. Copy environment file
cp .env.example .env

# 3. Spin up services (PostgreSQL + FastAPI + React Frontend)
docker compose up -d

# 4. Ingest transcripts into vector store
docker compose exec backend python /app/../ingestion/ingest.py

# 5. Access Frontend
Open http://localhost:5173 in your browser
```

---

## Running Locally Without Docker

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (with `pgvector` extension enabled, or SQLite fallback mode)
- Ollama (Optional for local LLM evaluation: `ollama run llama3.2`)

### 1. Database Setup
```bash
createdb lenny_growth
psql -d lenny_growth -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy .env
cp ../.env.example .env

# Ingest Transcripts
python ../ingestion/ingest.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
Backend API will be live at `http://localhost:8000` (Docs: `http://localhost:8000/docs`).

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be live at `http://localhost:5173`.

---

## Ollama Local LLM Configuration

To evaluate the application locally using Ollama:
1. Download Ollama from [ollama.com](https://ollama.com).
2. Pull the default model:
   ```bash
   ollama pull llama3.2
   ```
3. Verify Ollama is running at `http://localhost:11434`.
4. In `.env` or via the UI top bar / sidebar, ensure `LLM_PROVIDER=ollama`.

If Ollama is offline or unavailable, the backend automatically triggers fallback to Anthropic/OpenAI if API keys are present in `.env`.

---

## Running Automated Tests

```bash
cd backend
pytest tests/
```

Runs test suites covering:
- FastAPI health & session CRUD endpoints (`test_api.py`)
- RAG vector retriever & empty retrieval boundaries (`test_retrieval.py`)
- Agent Router classification & tool dispatching (`test_agent.py`)

---

## Project Architecture

```text
The Lenny Growth Assistant/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI REST endpoints
│   │   ├── agents/       # Agent Router & intent classifier
│   │   ├── skills/       # Ship 30 & Artifact generation skills
│   │   ├── rag/          # Embeddings & vector retriever
│   │   ├── services/     # LLM provider abstraction & HTML security
│   │   ├── db/           # SQLAlchemy models & database connection
│   │   ├── config/       # Pydantic settings
│   │   └── main.py       # FastAPI application entry point
│   ├── tests/            # Pytest automated test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React components (ArtifactViewer, ChatMessage, Sidebar)
│   │   ├── services/     # REST API client
│   │   ├── types/        # TypeScript interfaces
│   │   └── App.tsx       # Main layout & state manager
│   ├── package.json
│   └── Dockerfile
├── ingestion/
│   └── ingest.py         # Transcript chunking & vector indexing pipeline
├── docs/                 # Product & Architecture specs
├── docker-compose.yml
├── .env.example
├── README.md
├── PRD.md
├── design.md
└── architecture.md
```

---

## Troubleshooting & FAQ

- **PostgreSQL Connection Error**: If Postgres is offline, the backend automatically logs a warning and falls back to an embedded SQLite vector database for zero-downtime demonstration.
- **Ollama Connection Timeout**: Ensure `OLLAMA_BASE_URL` matches your host environment (`http://localhost:11434` for local dev or `http://host.docker.internal:11434` when running backend inside Docker).
- **Missing API Keys**: Cloud providers require `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`. The UI displays health check icons for each provider.
