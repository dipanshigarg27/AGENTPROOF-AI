"""
AgentProof AI — Report Generator Service
Generates the final Trust Report from evaluation results.
Recommendation text is derived from actual evaluation scores, not hardcoded.
"""
import logging
from typing import Optional

logger = logging.getLogger("agentproof.report")


def generate_recommendation(model_scores: list[dict], task: str) -> str:
    """
    Generate a recommendation paragraph based on actual scores.
    Never uses hardcoded text — always references real model names and scores.
    """
    if not model_scores:
        return "No models completed evaluation successfully."

    # Sort by trust score (primary), efficiency score (secondary)
    sorted_by_trust = sorted(model_scores, key=lambda x: x.get("trust_score", 0), reverse=True)
    sorted_by_efficiency = sorted(model_scores, key=lambda x: x.get("efficiency_score", 0), reverse=True)

    best_trust = sorted_by_trust[0]
    best_efficiency = sorted_by_efficiency[0]

    best_trust_name = best_trust["display_name"]
    best_efficiency_name = best_efficiency["display_name"]

    trust_score = best_trust.get("trust_score", 0)
    efficiency_score = best_efficiency.get("efficiency_score", 0)

    recommendation = []

    # Primary recommendation based on trust
    if trust_score >= 70:
        recommendation.append(
            f"**{best_trust_name}** performed best on trustworthiness for this task "
            f"with a Trust Score of {trust_score:.1f}/100."
        )
    elif trust_score >= 40:
        recommendation.append(
            f"**{best_trust_name}** had the highest Trust Score ({trust_score:.1f}/100), "
            f"though several claims required further verification."
        )
    else:
        recommendation.append(
            f"No model achieved a high Trust Score for this task. "
            f"**{best_trust_name}** scored highest at {trust_score:.1f}/100, "
            f"but many claims could not be verified or were contradicted by evidence."
        )

    # Efficiency note
    if best_efficiency_name != best_trust_name:
        eff_trust = best_efficiency.get("trust_score", 0)
        recommendation.append(
            f"**{best_efficiency_name}** was the most efficient model "
            f"(Efficiency Score: {efficiency_score:.1f}/100) but had a lower Trust Score of {eff_trust:.1f}/100. "
            f"Consider this trade-off when selecting a model for production use."
        )
    else:
        recommendation.append(
            f"**{best_trust_name}** was also the most efficient model "
            f"(Efficiency Score: {efficiency_score:.1f}/100), making it the overall recommended choice."
        )

    # Per-model summary (brief)
    if len(sorted_by_trust) > 1:
        summaries = []
        for m in sorted_by_trust:
            verified = m.get("verified_claims", 0)
            contradicted = m.get("contradicted_claims", 0)
            latency = m.get("latency_ms")
            latency_str = f"{latency:.0f}ms response time" if latency else "response time unavailable"
            summaries.append(
                f"• **{m['display_name']}**: {verified} verified, {contradicted} contradicted claims, {latency_str}"
            )
        recommendation.append("\n\nModel comparison:\n" + "\n".join(summaries))

    recommendation.append(
        "\n\n*Note: Trust Scores reflect claim verification against available web evidence at the time of evaluation. "
        "They are not a comprehensive measure of model accuracy or reliability.*"
    )

    return " ".join(recommendation)


def generate_report(
    evaluation_id: str,
    task: str,
    task_category: str,
    model_results: list[dict],
) -> dict:
    """
    Generate the complete Trust Report from evaluation results.
    
    Args:
        model_results: list of dicts, each with keys:
            model_id, display_name, response_text, latency_ms,
            total_tokens, estimated_cost_usd, trust_score, efficiency_score,
            task_completion_score, verified_claims, contradicted_claims,
            outdated_claims, unverifiable_claims, opinion_claims, total_claims,
            trust_score_explanation, efficiency_score_explanation,
            claims (list of verified claim dicts)
    
    Returns complete report dict.
    """
    successful_models = [m for m in model_results if m.get("response_text")]
    failed_models = [m for m in model_results if not m.get("response_text")]

    recommendation = generate_recommendation(successful_models, task)

    # Find best and worst performers
    if successful_models:
        best_trust_model = max(successful_models, key=lambda x: x.get("trust_score", 0))
        best_efficiency_model = max(successful_models, key=lambda x: x.get("efficiency_score", 0))
    else:
        best_trust_model = None
        best_efficiency_model = None

    return {
        "evaluation_id": evaluation_id,
        "task": task,
        "task_category": task_category,
        "recommendation": recommendation,
        "best_trust_model": best_trust_model["display_name"] if best_trust_model else None,
        "best_efficiency_model": best_efficiency_model["display_name"] if best_efficiency_model else None,
        "models": model_results,
        "failed_models": [{"model_id": m["model_id"], "error": m.get("error")} for m in failed_models],
        "scoring_methodology": {
            "trust_score": (
                "Trust Score (0–100) = (verified_ratio × 100) − (contradicted × 15) "
                "− (outdated × 8) − (unverifiable × 3) + (task_completion × 20). "
                "Opinions and predictions are excluded from factual scoring. "
                "Score is not a guarantee of truth."
            ),
            "efficiency_score": (
                "Efficiency Score (0–100) = weighted average of latency score "
                "(weight 50%), token efficiency (30%), and cost efficiency (20%). "
                "Missing metrics are excluded from weighting with an explanation."
            ),
        },
    }
