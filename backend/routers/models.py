"""AgentProof AI — Models Router
Lists available AI models based on configured API keys.
"""
import os
import logging
from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger("agentproof.models")

# ---------------------------------------------------------------------------
# Model Registry
#
# model_id format: "<provider>/<model-name>"
#   - provider must match a key in DIRECT_BASE_URLS in bifrost_service.py
#   - when using Bifrost, the full "provider/model" string is sent
#   - when calling directly, only the model name is sent to the provider's API
#
# env_key: the environment variable that must be set to use this model
# ---------------------------------------------------------------------------

ALL_MODELS = [
    # ── OpenAI ───────────────────────────────────────────────────────────────
    {
        "id": "openai/gpt-4o-mini",
        "provider": "openai",
        "display_name": "GPT-4o Mini",
        "description": "Fast, cost‑efficient OpenAI model. Good for extraction and verification tasks.",
        "context_window": 128000,
        "cost_per_million_input": 0.15,
        "cost_per_million_output": 0.60,
        "env_key": "OPENAI_API_KEY",
    },
    {
        "id": "openai/gpt-4o",
        "provider": "openai",
        "display_name": "GPT-4o",
        "description": "OpenAI flagship model. High accuracy, higher cost.",
        "context_window": 128000,
        "cost_per_million_input": 2.50,
        "cost_per_million_output": 10.00,
        "env_key": "OPENAI_API_KEY",
    },
    {
        "id": "openai/gpt-3.5-turbo",
        "provider": "openai",
        "display_name": "GPT-3.5 Turbo",
        "description": "Classic fast model from OpenAI.",
        "context_window": 16385,
        "cost_per_million_input": 0.50,
        "cost_per_million_output": 1.50,
        "env_key": "OPENAI_API_KEY",
    },
    # ── Anthropic ────────────────────────────────────────────────────────────
    {
        "id": "anthropic/claude-3-haiku-20240307",
        "provider": "anthropic",
        "display_name": "Claude 3 Haiku",
        "description": "Anthropic's fastest model. Great for high‑volume tasks.",
        "context_window": 200000,
        "cost_per_million_input": 0.25,
        "cost_per_million_output": 1.25,
        "env_key": "ANTHROPIC_API_KEY",
    },
    {
        "id": "anthropic/claude-3-5-haiku-20241022",
        "provider": "anthropic",
        "display_name": "Claude 3.5 Haiku",
        "description": "Anthropic's latest efficient model with improved reasoning.",
        "context_window": 200000,
        "cost_per_million_input": 0.80,
        "cost_per_million_output": 4.00,
        "env_key": "ANTHROPIC_API_KEY",
    },
    {
        "id": "anthropic/claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "display_name": "Claude 3.5 Sonnet",
        "description": "Anthropic's best balance of intelligence and speed.",
        "context_window": 200000,
        "cost_per_million_input": 3.00,
        "cost_per_million_output": 15.00,
        "env_key": "ANTHROPIC_API_KEY",
    },
    # ── Groq ─────────────────────────────────────────────────────────────────
    {
        "id": "groq/llama-3.3-70b-versatile",
        "provider": "groq",
        "display_name": "Llama 3.3 70B (Groq)",
        "description": "Large, capable open model on Groq's fast inference platform.",
        "context_window": 131072,
        "cost_per_million_input": 0.59,
        "cost_per_million_output": 0.79,
        "env_key": "GROQ_API_KEY",
    },
    {
        "id": "groq/mixtral-8x7b-32768",
        "provider": "groq",
        "display_name": "Mixtral 8x7B (Groq)",
        "description": "MoE model with 32K context, fast on Groq.",
        "context_window": 32768,
        "cost_per_million_input": 0.24,
        "cost_per_million_output": 0.24,
        "env_key": "GROQ_API_KEY",
    },
    # ── Added Groq Qwen model (no extra prefix) ───────────────────────────────
    {
        "id": "qwen/qwen3.8-27b",
        "provider": "groq",
        "display_name": "Qwen 3.8B (Groq)",
        "description": "High‑capacity Groq model for complex reasoning.",
        "context_window": 131072,
        "cost_per_million_input": 0.45,
        "cost_per_million_output": 0.60,
        "env_key": "GROQ_API_KEY",
    },
    # ── OpenAI OSS models via Groq ─────────────────────────────────────────────
    {
        "id": "openai/gpt-oss-safeguard-20b",
        "provider": "groq",
        "display_name": "GPT OSS Safeguard 20B (Groq)",
        "description": "OpenAI OSS 20B model with safety guard, routed via Groq.",
        "context_window": 131072,
        "cost_per_million_input": 0.075,
        "cost_per_million_output": 0.30,
        "env_key": "GROQ_API_KEY",
    },
    {
        "id": "openai/gpt-oss-120b",
        "provider": "groq",
        "display_name": "GPT OSS 120B (Groq)",
        "description": "OpenAI OSS 120B model routed through Groq.",
        "context_window": 131072,
        "env_key": "GROQ_API_KEY",
    },
]

def _is_key_configured(env_key: str) -> bool:
    """Return True only if the env var looks like a real API key."""
    value = os.getenv(env_key, "")
    if not value or len(value) < 15:
        return False
    if "xxx" in value.lower():
        return False
    return True

@router.get("/models")
async def list_models():
    """Return all models with their availability status.
    Only marks a model as available if the required API key is configured.
    """
    result = []
    for model in ALL_MODELS:
        available = _is_key_configured(model["env_key"])
        entry = {**model, "available": available}
        if not available:
            entry["unavailable_reason"] = (
                f"Set {model['env_key']} in backend/.env to enable this model."
            )
        result.append(entry)
    return {"models": result}
