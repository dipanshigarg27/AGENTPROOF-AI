# 🛡️ AgentProof AI

### Evaluate AI. Verify Facts. Build Trust.

AgentProof AI is an AI agent evaluation and benchmarking platform designed to help users understand how different AI models perform when given the same task.

Instead of judging AI responses only by how convincing they sound, AgentProof AI aims to evaluate their factual reliability, response quality, speed, token usage, and estimated cost.

It also uses live web evidence through **Tavily Search** to help check factual claims and identify potentially outdated or unsupported information.

---

## 🚨 The Problem

AI models can produce answers that sound confident but contain inaccurate, outdated, or unsupported information.

Users often have no simple way to compare multiple models, understand which responses are more reliable, or evaluate the trade-off between accuracy, speed, and cost.

## 💡 Our Solution

AgentProof AI provides a unified evaluation workspace where users can:

- Submit one task or question.
- Compare multiple AI models using the same input.
- Measure response time and token consumption.
- Extract factual claims from AI-generated responses.
- Check claims against live web evidence using Tavily.
- Analyse trust and efficiency indicators.
- Generate evaluation reports.

Our goal is to make AI performance more transparent, measurable, and easier to understand.

---

## ✨ Key Features

### 1. Multi-Model Benchmarking
Compare multiple AI models using identical prompts and evaluation conditions.

### 2. Factual Claim Extraction
Identify factual statements in AI-generated responses for further verification.

### 3. Live Web Verification
Use Tavily Search to retrieve relevant web evidence and assess claims.

### 4. Trust Score
Provide an indicative trust score based on verification outcomes and available evidence.

### 5. Efficiency Score
Evaluate model efficiency using available performance metrics, including:
- Response latency
- Token consumption
- Estimated API cost

### 6. Evaluation Reports
Present model responses, verification outcomes, and performance comparisons in a structured report.

---

## 🏗️ How It Works

1. **Enter a Task:** The user submits a question or task.
2. **Select Models:** Choose the AI models to compare.
3. **Generate Responses:** Selected models receive the same task.
4. **Extract Claims:** Factual claims are identified from the responses.
5. **Verify Evidence:** Tavily retrieves relevant live web sources for claim verification.
6. **Calculate Scores:** Trust and efficiency indicators are calculated from available results.
7. **View Results:** Review the comparison and evaluation report.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| Database | SQLite |
| AI Integration | OpenAI-compatible APIs |
| Web Search | Tavily Search API |
| Data Validation | Pydantic |
| Testing | Pytest |

---

## 📁 Project Structure

```text
AGENTPROOF AI/
│
├── backend/
│   ├── routers/
│   │   ├── evaluations.py
│   │   └── models.py
│   │
│   ├── services/
│   │   ├── bifrost_service.py
│   │   ├── claim_extractor.py
│   │   ├── claim_verifier.py
│   │   ├── scoring.py
│   │   ├── tavily_service.py
│   │   └── report_generator.py
│   │
│   ├── tests/
│   ├── main.py
│   ├── database.py
│   └── requirements.txt
│
└── frontend/
    ├── src/
    ├── public/
    └── package.json
```

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.12+
- Node.js and npm
- API keys for the providers you intend to use
- Tavily API key

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd "AGENTPROOF AI"
```

### 2. Configure the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file inside the backend folder and configure the required API keys using the variable names expected by the application.

**Never upload your `.env` file or expose API keys publicly.**

### 3. Start the backend

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Backend API documentation:

```text
http://localhost:8000/docs
```

### 4. Start the frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your terminal.

---

## 🔐 Security

- API keys should be stored in environment variables.
- Never commit `.env` files.
- Do not expose private credentials in screenshots, logs, or public repositories.

## ⚠️ Evaluation Disclaimer

Trust and efficiency scores are indicative evaluation metrics, not guarantees of factual correctness.

Web evidence availability, source quality, model-provider responses, and API limitations can affect verification results. Claims without sufficient evidence should not be presented as verified.

## 🎯 Project Vision

AgentProof AI aims to move AI evaluation beyond response generation towards measurable performance, evidence-based verification, and greater transparency.

**Don't just ask AI. Evaluate it. Verify it. Trust it responsibly.**

---

*Built as a hackathon project exploring AI agent benchmarking, factual verification, and responsible AI evaluation.*
