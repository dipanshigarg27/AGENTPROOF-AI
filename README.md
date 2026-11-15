# AgentProof AI — Setup Guide

**Don't Just Compare AI Agents. Verify Their Answers.**

> Hackathon prototype for Bifrost PS02 (AI Agent Benchmarking) + Tavily PS06 (Stale Answer Detector)

---

## What You Need

| Service | Where to Get It | Required? |
|---|---|---|
| Tavily API Key | https://tavily.com | ✅ Required for claim verification |
| OpenAI API Key | https://platform.openai.com/api-keys | At least ONE of these |
| Anthropic API Key | https://console.anthropic.com/settings/keys | At least ONE |
| Groq API Key (free) | https://console.groq.com/keys | At least ONE |
| Docker (for Bifrost) | https://docker.com | Optional — app works without it |
| Python 3.11+ | https://python.org | ✅ Required for backend |
| Node.js 18+ | https://nodejs.org | ✅ Required for frontend |

---

## Step 1 — Add Your API Keys

```bash
# Copy the template
cp .env.example backend/.env

# Open backend/.env and fill in your keys:
# TAVILY_API_KEY=tvly-your-key-here
# OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# GROQ_API_KEY=gsk_your-key-here
```

> Never commit `backend/.env` to Git. It's already in `.gitignore`.

---

## Step 2 — (Optional) Start Bifrost Gateway

Bifrost routes requests through a single OpenAI-compatible API, adding fallbacks and load balancing.

If you have Docker installed:

```bash
# From the project root
docker compose up -d

# Check it's running
curl http://localhost:8080/health
```

If Docker is not available, the app will connect **directly to provider APIs** automatically. No action needed.

---

## Step 3 — Start the Backend

```bash
cd backend

# Create and activate virtual environment (first time only)
python3 -m venv venv
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the backend
python main.py
# OR: uvicorn main:app --reload --port 8000
```

The backend starts at **http://localhost:8000**

Verify it's running:
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/models
```

---

## Step 4 — Start the Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

The frontend starts at **http://localhost:5173**

---

## Step 5 — Run Your First Evaluation

1. Open **http://localhost:5173**
2. Click **"Start Evaluating"**
3. Enter a question (e.g., *"What is the current Fed interest rate?"*)
4. Select 2+ available models (shown in green)
5. Click **"Run Evaluation"**
6. Watch the 7-stage progress tracker
7. View the Comparison Dashboard → Claim Report → Trust Report

---

## Demo Mode (No API Keys Needed)

If you haven't added API keys yet, you can still explore the UI:

1. Click **"Demo"** in the navbar
2. Navigate through the sample evaluation
3. All demo data is clearly labelled — no real API calls are made

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/api/health` | Health check + API key status |
| GET | `/api/models` | List configured models |
| POST | `/api/evaluations` | Start new evaluation |
| GET | `/api/evaluations/{id}` | Get evaluation status + results |
| GET | `/api/evaluations/{id}/report` | Get Trust Report |
| GET | `/api/evaluations/demo` | Get pre-prepared demo data |

---

## Project Structure

```
AGENTPROOF AI/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── database.py                # SQLite schema
│   ├── demo_data.py               # Pre-prepared demo evaluation
│   ├── requirements.txt
│   ├── .env                       # Your API keys (never commit)
│   ├── routers/
│   │   ├── evaluations.py         # Full evaluation pipeline
│   │   └── models.py              # Model availability
│   └── services/
│       ├── bifrost_service.py     # Bifrost / direct API calls
│       ├── tavily_service.py      # Live web evidence
│       ├── claim_extractor.py     # LLM-based claim extraction
│       ├── claim_verifier.py      # Claim vs evidence comparison
│       ├── scoring.py             # Trust + Efficiency formulas
│       └── report_generator.py    # Trust Report builder
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── EvaluationWorkspace.jsx
│   │   │   ├── EvaluationProgress.jsx
│   │   │   ├── ComparisonDashboard.jsx
│   │   │   ├── ClaimVerificationReport.jsx
│   │   │   ├── TrustReport.jsx
│   │   │   └── DemoPage.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── ScoreRing.jsx
│   │   │   ├── ClaimBadge.jsx
│   │   │   └── SourceCard.jsx
│   │   └── lib/api.js
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml             # Bifrost gateway
├── .env.example                   # API key template
└── README.md
```

---

## Scoring Methodology

### Trust Score (0–100)
```
score = (verified / total_factual × 100)
      − (contradicted × 15)
      − (outdated × 8)
      − (unverifiable × 3)
      + (task_completion × 20)
```
Opinions and predictions are excluded. Score ≠ guarantee of truth.

### Efficiency Score (0–100)
```
latency_score = max(0, 100 − latency_ms / 100)   [weight: 50%]
token_score   = max(0, 100 − total_tokens / 50)   [weight: 30%]
cost_score    = max(0, 100 − cost_usd × 10000)    [weight: 20%]
```
Missing metrics are excluded from weighting with an explanation.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "No models available" | Add at least one API key to `backend/.env` |
| "Tavily error" | Check TAVILY_API_KEY in `.env` |
| Backend fails to start | Run `pip install -r requirements.txt` in the backend venv |
| Frontend won't connect | Make sure backend is running on port 8000 |
| Bifrost connection refused | Either start Docker or leave BIFROST_BASE_URL blank (direct mode) |

---

## Security Notes

- API keys are stored server-side only — never sent to the frontend
- Retrieved web content is treated as untrusted evidence, never executed
- Stack traces are never exposed to users
- `.env` is in `.gitignore` — never commit it
