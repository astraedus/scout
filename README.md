# Scout — Company Research Agent

Scout is an AI-powered company research agent built for the Amazon Nova AI Hackathon. It uses Nova Act for browser automation and Nova 2 Lite (via AWS Bedrock) for synthesis.

## Architecture

```
frontend/          Next.js dashboard (port 3000)
backend/           FastAPI Python backend (port 8000)
  extractors/      Nova Act browser extractors (website, LinkedIn, Crunchbase, news, careers)
  synthesis/       Nova 2 Lite AI briefing synthesis
  models/          Pydantic data models
  db/              SQLite storage
scripts/           Test scripts for Nova Act and Bedrock
```

## Quickstart

### 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Run the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

### 3. Test connections

```bash
python scripts/hello_nova_act.py    # Test Nova Act
python scripts/hello_bedrock.py     # Test Bedrock Nova 2 Lite
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/research` | Start research for a company |
| GET | `/api/research/{id}` | Get research status and results |
| GET | `/api/research/{id}/stream` | SSE stream for live progress |
| GET | `/api/history` | Get recent research history |
| GET | `/health` | Health check |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NOVA_ACT_API_KEY` | Nova Act API key |
| `AWS_ACCESS_KEY_ID` | AWS credentials for Bedrock |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for Bedrock |
| `AWS_REGION` | AWS region (default: us-east-1) |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend (default: http://localhost:8000) |
