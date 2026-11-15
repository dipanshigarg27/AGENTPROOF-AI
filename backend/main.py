"""
AgentProof AI — FastAPI Backend
Main application entry point
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import init_db
from routers import evaluations, models

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agentproof")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    logger.info("Starting AgentProof AI backend...")
    await init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down AgentProof AI backend.")


app = FastAPI(
    title="AgentProof AI",
    description="AI Agent Benchmarking Platform — Compare, Verify, Trust",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evaluations.router, prefix="/api")
app.include_router(models.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """Health check with API key status and Bifrost reachability (never exposes actual keys)."""
    import httpx
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    bifrost_url = os.getenv("BIFROST_BASE_URL", "http://localhost:8080")

    def _key_ok(val):
        return bool(val and len(val) >= 15 and "xxx" not in val.lower())

    # Check Bifrost reachability (only 2xx = healthy)
    bifrost_healthy = False
    bifrost_status_code = None
    bifrost_error = None
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{bifrost_url}/health")
            bifrost_status_code = resp.status_code
            bifrost_healthy = 200 <= resp.status_code < 300
            if not bifrost_healthy:
                bifrost_error = f"HTTP {resp.status_code} — not treating as healthy"
    except Exception as exc:
        bifrost_error = str(exc)

    return {
        "status": "ok",
        "version": "1.0.0",
        "api_keys": {
            "tavily": _key_ok(tavily_key),
            "openai": _key_ok(openai_key),
            "anthropic": _key_ok(anthropic_key),
            "groq": _key_ok(groq_key),
        },
        "bifrost": {
            "url": bifrost_url,
            "healthy": bifrost_healthy,
            "status_code": bifrost_status_code,
            "error": bifrost_error,
            "note": (
                "Bifrost is reachable and will be used for model calls."
                if bifrost_healthy
                else "Bifrost unavailable — model calls will use direct provider APIs."
            ),
        },
        "demo_mode_available": True,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True,
    )
