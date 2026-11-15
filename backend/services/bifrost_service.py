"""
AgentProof AI — Bifrost / Direct Provider Service

Calls AI models through the Bifrost gateway (OpenAI-compatible) when it is
reachable, otherwise directly through the provider API (Groq, etc.).

Rules enforced here:
- An empty / None / whitespace-only answer is a FAILURE, never a success.
- Every code path returns the same result shape.
- `truncated` is True when the provider stopped because of the token limit.
- API keys are never put into error messages or logs.
"""
import os
import time
import logging
import asyncio
from typing import Optional

import httpx
from openai import AsyncOpenAI

logger = logging.getLogger("agentproof.bifrost")

# Provider base URLs for direct calls
DIRECT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com/v1",
    "groq": "https://api.groq.com/openai/v1",
}

# API key env var names per provider
PROVIDER_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
}

# Model ids that are hosted on Groq even though they do not start with "groq/".
# They are sent to Groq with their FULL id (e.g. "openai/gpt-oss-120b").
GROQ_HOSTED_PREFIXES = ("openai/gpt-oss", "qwen/", "meta-llama/", "moonshotai/")

# Reasoning models spend tokens "thinking" before they write the visible answer.
# With a small max_tokens they can return an empty answer, so give them a floor.
REASONING_MODEL_MARKERS = ("gpt-oss", "qwen3", "safeguard")
REASONING_MIN_TOKENS = 1500

# Cost per 1M tokens (USD). Only models listed here get a cost estimate;
# everything else is None (we never guess a cost).
COST_TABLE = {
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "openai/gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "openai/gpt-4o": {"input": 2.50, "output": 10.00},
    "anthropic/claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "anthropic/claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
    "anthropic/claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "groq/llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
    "groq/llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
    "groq/mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
}

_bifrost_cache = {"ok": None, "at": 0.0}
_BIFROST_CACHE_SECONDS = 30


def _redact(text) -> str:
    """Remove any configured API key values from a string before it is stored or logged."""
    out = str(text)
    env_names = list(PROVIDER_ENV_KEYS.values()) + ["BIFROST_API_KEY", "TAVILY_API_KEY"]
    for env_name in env_names:
        secret = os.getenv(env_name, "")
        if secret and len(secret) > 8:
            out = out.replace(secret, "[REDACTED]")
    return out


async def _check_bifrost_available() -> bool:
    """
    True only if the Bifrost gateway answers its /health endpoint with a 2xx.
    Connection errors, timeouts and non-2xx answers all mean "not available".
    The result is cached for a few seconds so parallel model calls do not
    each wait for their own health check.
    """
    now = time.time()
    if _bifrost_cache["ok"] is not None and now - _bifrost_cache["at"] < _BIFROST_CACHE_SECONDS:
        return _bifrost_cache["ok"]

    bifrost_url = os.getenv("BIFROST_BASE_URL", "http://localhost:8080")
    ok = False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{bifrost_url}/health")
            ok = 200 <= resp.status_code < 300
            if not ok:
                logger.warning(
                    f"Bifrost health check returned HTTP {resp.status_code} — "
                    f"treating gateway as UNAVAILABLE. Using direct provider APIs."
                )
    except Exception as exc:
        logger.warning(f"Bifrost unreachable ({_redact(exc)}) — using direct provider APIs.")
        ok = False

    _bifrost_cache["ok"] = ok
    _bifrost_cache["at"] = now
    return ok


def _effective_max_tokens(model_id: str, max_tokens: int) -> int:
    """Raise max_tokens for reasoning models so they can finish thinking AND answer."""
    lowered = model_id.lower()
    if any(marker in lowered for marker in REASONING_MODEL_MARKERS):
        return max(max_tokens, REASONING_MIN_TOKENS)
    return max_tokens


def _get_client_for_model(model_id: str, use_bifrost: bool) -> tuple[AsyncOpenAI, str]:
    """
    Returns (AsyncOpenAI client, model string to send).

    Bifrost reachable -> route through Bifrost with the 'provider/model' id.
    Otherwise         -> call the provider directly with its own model name.
    Raises ValueError if the needed API key is missing.
    """
    provider = model_id.split("/")[0] if "/" in model_id else "openai"
    model_name = model_id.split("/", 1)[1] if "/" in model_id else model_id

    # Groq-hosted models whose ids do not start with "groq/"
    if provider != "groq" and model_id.startswith(GROQ_HOSTED_PREFIXES) and os.getenv("GROQ_API_KEY"):
        provider = "groq"
        model_name = model_id

    if use_bifrost:
        bifrost_url = os.getenv("BIFROST_BASE_URL", "http://localhost:8080")
        bifrost_key = os.getenv("BIFROST_API_KEY") or "dummy-key"
        client = AsyncOpenAI(
            base_url=f"{bifrost_url}/v1",
            api_key=bifrost_key,
            max_retries=3,
            timeout=60.0,
        )
        return client, model_id

    api_key_env = PROVIDER_ENV_KEYS.get(provider, "OPENAI_API_KEY")
    api_key = os.getenv(api_key_env, "")
    if not api_key:
        raise ValueError(f"Missing {api_key_env} in backend/.env (needed for provider '{provider}').")
    base_url = DIRECT_BASE_URLS.get(provider, "https://api.openai.com/v1")
    client = AsyncOpenAI(base_url=base_url, api_key=api_key, max_retries=3, timeout=60.0)
    return client, model_name


def _estimate_cost(model_id: str, prompt_tokens, completion_tokens) -> Optional[float]:
    """Estimate cost from token counts. None if the model is not in the table."""
    costs = COST_TABLE.get(model_id)
    if not costs or prompt_tokens is None or completion_tokens is None:
        return None
    return (prompt_tokens * costs["input"] + completion_tokens * costs["output"]) / 1_000_000


def _build_result(
    *,
    status: str,
    response_text: Optional[str],
    latency_ms: float,
    prompt_tokens=None,
    completion_tokens=None,
    total_tokens=None,
    estimated_cost_usd=None,
    finish_reason: Optional[str] = None,
    error: Optional[str] = None,
    truncated: bool = False,
    used_bifrost: bool = False,
    route: str = "",
) -> dict:
    """One consistent result shape for every code path."""
    return {
        "status": status,  # "completed" or "failed"
        "response_text": response_text,
        "latency_ms": round(latency_ms, 2),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": estimated_cost_usd,
        "finish_reason": finish_reason,
        "truncated": truncated,
        "error": error,
        "used_bifrost": used_bifrost,
        "routed_via": "bifrost" if used_bifrost else "direct",
        "route": route,
    }


async def call_model(
    model_id: str,
    task: str,
    max_tokens: int = 1000,
    system_prompt: Optional[str] = None,
) -> dict:
    """
    Call one AI model. Always returns the dict from _build_result().
    status == "completed" only when real, non-empty text came back.
    """
    use_bifrost = await _check_bifrost_available()
    route_label = "Bifrost gateway" if use_bifrost else "direct provider API (Bifrost unavailable)"
    logger.info(f"Calling model {model_id} via {route_label}")

    start_time = time.time()
    try:
        client, model_string = _get_client_for_model(model_id, use_bifrost)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": task})

        response = await client.chat.completions.create(
            model=model_string,
            messages=messages,
            max_tokens=_effective_max_tokens(model_id, max_tokens),
            temperature=0.3,
        )
        latency_ms = (time.time() - start_time) * 1000

        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else None
        completion_tokens = usage.completion_tokens if usage else None
        total_tokens = usage.total_tokens if usage else None
        estimated_cost = _estimate_cost(model_id, prompt_tokens, completion_tokens)

        if not response.choices:
            return _build_result(
                status="failed", response_text=None, latency_ms=latency_ms,
                prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                total_tokens=total_tokens, estimated_cost_usd=estimated_cost,
                finish_reason="error", error="Provider returned no choices.",
                used_bifrost=use_bifrost, route=route_label,
            )

        choice = response.choices[0]
        text = choice.message.content
        finish_reason = choice.finish_reason
        truncated = finish_reason == "length"

        # Empty / None / whitespace-only is a failure, never a success.
        if text is None or not str(text).strip():
            reason = "Empty response from provider."
            if truncated:
                reason = (
                    "Empty response: the model hit the token limit before writing "
                    "any visible text. Try a higher max_tokens."
                )
            logger.error(f"Model {model_id} failed via {route_label}: {reason}")
            return _build_result(
                status="failed", response_text=None, latency_ms=latency_ms,
                prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                total_tokens=total_tokens, estimated_cost_usd=estimated_cost,
                finish_reason=finish_reason, error=reason, truncated=truncated,
                used_bifrost=use_bifrost, route=route_label,
            )

        return _build_result(
            status="completed", response_text=text, latency_ms=latency_ms,
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
            total_tokens=total_tokens, estimated_cost_usd=estimated_cost,
            finish_reason=finish_reason, error=None, truncated=truncated,
            used_bifrost=use_bifrost, route=route_label,
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        safe_error = _redact(e)
        logger.error(f"Model {model_id} failed via {route_label}: {safe_error}")
        return _build_result(
            status="failed", response_text=None, latency_ms=latency_ms,
            finish_reason="error", error=safe_error,
            used_bifrost=use_bifrost, route=route_label,
        )


async def call_models_concurrently(
    model_ids: list[str],
    task: str,
    max_tokens: int = 1000,
    system_prompt: Optional[str] = None,
) -> dict[str, dict]:
    """Call several models in parallel. One failure never affects the others."""
    tasks = [call_model(model_id, task, max_tokens, system_prompt) for model_id in model_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    out: dict[str, dict] = {}
    for model_id, result in zip(model_ids, results):
        if isinstance(result, Exception):
            out[model_id] = _build_result(
                status="failed", response_text=None, latency_ms=0.0,
                finish_reason="error", error=_redact(result),
            )
        else:
            out[model_id] = result
    return out

