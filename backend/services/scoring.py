"""
AgentProof AI — Scoring Service
Calculates Trust Score and Efficiency Score with full transparency.

TRUST SCORE (0–100), only for models that returned a real answer:
  checkable = SUPPORTED + CONTRADICTED + POTENTIALLY_OUTDATED
  verified_ratio = SUPPORTED / checkable
  trust = verified_ratio * 100
          - contradicted * 15
          - outdated * 8
          + task_completion * 20
  clamped to 0–100.

  Notes:
    - UNVERIFIABLE claims are NOT counted as wrong: absence of evidence is not
      evidence of error. They are reported, but excluded from the score.
    - OPINION claims are not factual claims and are excluded.
    - If there are no checkable claims, the score is None (not scored) rather
      than an invented number.
    - The score is not a guarantee of truth.

EFFICIENCY SCORE (0–100):
    latency_score = max(0, 100 - latency_ms / 100)    # 0 ms -> 100, 10 000 ms -> 0
    token_score   = max(0, 100 - total_tokens / 50)   # 5 000 tokens -> 0
    cost_score    = max(0, 100 - cost_usd * 10000)    # $0.01 -> 0
    weights: latency 0.5, tokens 0.3, cost 0.2 (unavailable metrics are excluded
    and the remaining weights are re-normalised).
    If no metric is available, the score is None.

Both functions return (score_or_None, explanation_string).
"""
import logging
from typing import Optional

logger = logging.getLogger("agentproof.scoring")


def calculate_trust_score(
    verified_count: int,
    contradicted_count: int,
    outdated_count: int,
    unverifiable_count: int,
    opinion_count: int,
    total_claims: int,
    task_completion_score: float = 0.5,
) -> tuple[Optional[float], str]:
    """Returns (score 0–100 or None, explanation)."""
    verified_count = max(0, verified_count or 0)
    contradicted_count = max(0, contradicted_count or 0)
    outdated_count = max(0, outdated_count or 0)
    unverifiable_count = max(0, unverifiable_count or 0)
    opinion_count = max(0, opinion_count or 0)
    task_completion_score = min(1.0, max(0.0, task_completion_score or 0.0))

    checkable = verified_count + contradicted_count + outdated_count

    if checkable == 0:
        return None, (
            "Trust Score not calculated: there were no checkable factual claims "
            f"({unverifiable_count} unverifiable, {opinion_count} opinion). "
            "A score would be misleading without verified evidence."
        )

    verified_ratio = verified_count / checkable
    base_score = verified_ratio * 100
    contradicted_penalty = contradicted_count * 15
    outdated_penalty = outdated_count * 8
    task_bonus = task_completion_score * 20

    raw_score = base_score - contradicted_penalty - outdated_penalty + task_bonus
    trust_score = max(0.0, min(100.0, raw_score))

    explanation = (
        f"Trust Score = ({verified_count}/{checkable} supported claims × 100) "
        f"− ({contradicted_count} contradicted × 15) "
        f"− ({outdated_count} outdated × 8) "
        f"+ (task completion {task_completion_score:.2f} × 20) "
        f"= {trust_score:.1f}. "
        f"Unverifiable claims ({unverifiable_count}) and opinions ({opinion_count}) "
        f"are excluded from the score. This score is not a guarantee of truth."
    )
    return round(trust_score, 1), explanation


def calculate_efficiency_score(
    latency_ms: Optional[float],
    total_tokens: Optional[int],
    estimated_cost_usd: Optional[float],
) -> tuple[Optional[float], str]:
    """Returns (score 0–100 or None, explanation)."""
    components = {}
    weights = {}

    if latency_ms is not None and latency_ms >= 0:
        components["latency"] = round(max(0.0, 100.0 - latency_ms / 100.0), 1)
        weights["latency"] = 0.5

    if total_tokens is not None and total_tokens >= 0:
        components["tokens"] = round(max(0.0, 100.0 - total_tokens / 50.0), 1)
        weights["tokens"] = 0.3

    if estimated_cost_usd is not None and estimated_cost_usd >= 0:
        components["cost"] = round(max(0.0, 100.0 - estimated_cost_usd * 10000.0), 1)
        weights["cost"] = 0.2

    if not components:
        return None, (
            "Efficiency Score not calculated: latency, token count and cost "
            "are all unavailable."
        )

    total_weight = sum(weights[k] for k in components)
    efficiency_score = sum(components[k] * weights[k] / total_weight for k in components)
    efficiency_score = max(0.0, min(100.0, efficiency_score))

    parts = []
    if "latency" in components:
        parts.append(f"latency {latency_ms:.0f}ms → {components['latency']:.1f}pts (weight 50%)")
    if "tokens" in components:
        parts.append(f"{total_tokens} tokens → {components['tokens']:.1f}pts (weight 30%)")
    if "cost" in components:
        parts.append(f"${estimated_cost_usd:.5f} cost → {components['cost']:.1f}pts (weight 20%)")

    missing = []
    if "latency" not in components:
        missing.append("latency")
    if "tokens" not in components:
        missing.append("token count")
    if "cost" not in components:
        missing.append("cost estimate")
    missing_note = f" Missing metrics ({', '.join(missing)}) excluded." if missing else ""

    explanation = f"Efficiency Score: {' | '.join(parts)} = {efficiency_score:.1f}.{missing_note}"
    return round(efficiency_score, 1), explanation


def calculate_task_completion(response_text: Optional[str], task: str) -> tuple[float, str]:
    """
    Heuristic task-completion score (0.0–1.0) from response length, structure and
    keyword overlap. This is a surface heuristic, not an LLM judge.
    """
    if not response_text or not response_text.strip():
        return 0.0, "[HEURISTIC ESTIMATE] No response received — task completion scored as 0."

    word_count = len(response_text.split())

    if word_count < 20:
        return 0.3, f"[HEURISTIC ESTIMATE] Very short response ({word_count} words) — may be incomplete."

    length_score = min(0.4, word_count / 500)

    structure_score = 0.0
    if any(marker in response_text for marker in ["1.", "2.", "•", "-", "\n\n"]):
        structure_score = 0.1

    task_words = set(w.lower() for w in (task or "").split() if len(w) > 4)
    response_words = set(w.lower() for w in response_text.split())
    if task_words:
        overlap = len(task_words & response_words) / len(task_words)
        keyword_score = min(0.3, overlap * 0.5)
    else:
        keyword_score = 0.15

    base_completion = 0.2
    total = min(1.0, base_completion + length_score + structure_score + keyword_score)

    return round(total, 2), (
        f"[HEURISTIC ESTIMATE] Task completion estimated at {total:.0%} based on "
        f"response length ({word_count} words) and task keyword coverage. "
        f"This is a surface-level heuristic, not an LLM judge."
    )

