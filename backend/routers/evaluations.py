"""
AgentProof AI — Evaluations Router
Full evaluation pipeline:
  1. Accept task + model selection
  2. Run models concurrently (Bifrost if reachable, else direct provider)
  3. Extract claims            (only for models that returned real text)
  4. Verify claims via Tavily  (only for those claims)
  5. Calculate scores          (only when valid; otherwise None)
  6. Store results and return a structured report

Each model is handled independently: one model failing never affects another.
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Optional

import aiosqlite
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from database import DB_PATH
from demo_data import get_demo_evaluation
from services.bifrost_service import call_models_concurrently
from services.claim_extractor import extract_claims
from services.claim_verifier import verify_claims_batch
from services.scoring import calculate_trust_score, calculate_efficiency_score, calculate_task_completion
from services.report_generator import generate_report

router = APIRouter()
logger = logging.getLogger("agentproof.evaluations")


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class EvaluationRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    task: str = Field(..., min_length=10, max_length=4000)
    model_ids: list[str] = Field(..., min_length=2, max_length=5)
    task_category: str = "General Knowledge"
    max_tokens: int = Field(default=1000, ge=100, le=4000)
    custom_instructions: Optional[str] = None


class EvaluationResponse(BaseModel):
    evaluation_id: str
    status: str
    message: str


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _update_status(evaluation_id: str, status: str, error: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE evaluations SET status = ?, error_message = ? WHERE id = ?",
            (status, error, evaluation_id)
        )
        await db.commit()


def _model_failed(result: dict) -> bool:
    """A model result is a failure if it errored OR returned no real text."""
    if result.get("status") == "failed" or result.get("error"):
        return True
    text = result.get("response_text")
    return text is None or not str(text).strip()


def _max_claims() -> int:
    try:
        return max(1, int(os.getenv("MAX_CLAIMS_PER_MODEL", "3")))
    except ValueError:
        return 3


def _pick_judge_model(model_ids: list[str], model_results: dict) -> Optional[str]:
    """
    Model used for claim extraction + verification.
    Prefer JUDGE_MODEL from .env, which should NOT be one of the compared models
    (otherwise a model judges itself). Fall back to a compared model that actually
    answered, and warn.
    """
    judge = os.getenv("JUDGE_MODEL", "").strip()
    if judge:
        if judge in model_ids:
            logger.warning(
                f"JUDGE_MODEL '{judge}' is also one of the compared models — "
                f"the judge may favour itself. Use a different model for fairness."
            )
        return judge

    for model_id in model_ids:
        if not _model_failed(model_results[model_id]):
            logger.warning(
                f"JUDGE_MODEL is not set; using '{model_id}' (a compared model) as judge. "
                f"Set JUDGE_MODEL in backend/.env to an independent model."
            )
            return model_id
    return None


async def _store_claims(evaluation_id: str, model_id: str, claims: list[dict]):
    async with aiosqlite.connect(DB_PATH) as db:
        for claim in claims:
            await db.execute(
                """INSERT INTO claims
                   (evaluation_id, model_id, claim_text, claim_type, claim_index)
                   VALUES (?, ?, ?, ?, ?)""",
                (evaluation_id, model_id, claim["text"], claim["type"], claim["claim_index"])
            )
        await db.commit()


async def _store_verified_claims(evaluation_id: str, model_id: str, verified: list[dict]):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, claim_index FROM claims WHERE evaluation_id = ? AND model_id = ?",
            (evaluation_id, model_id)
        ) as cursor:
            claim_rows = await cursor.fetchall()
        claim_id_map = {row[1]: row[0] for row in claim_rows}

        for claim in verified:
            v = claim.get("verification") or {}
            claim_db_id = claim_id_map.get(claim.get("claim_index"))
            if not claim_db_id:
                continue
            cur = await db.execute(
                """INSERT INTO verification_results
                   (claim_id, status, explanation, evidence_summary, retrieved_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    claim_db_id,
                    v.get("status", "UNVERIFIABLE"),
                    v.get("explanation", ""),
                    v.get("evidence_summary", ""),
                    v.get("retrieved_at", datetime.utcnow().isoformat() + "Z"),
                )
            )
            ver_id = cur.lastrowid
            if ver_id:
                for src in v.get("sources", []) or []:
                    await db.execute(
                        """INSERT INTO evidence_sources
                           (verification_id, title, url, snippet, published_date, relevance_score)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            ver_id,
                            src.get("title"),
                            src.get("url", ""),
                            src.get("snippet", ""),
                            src.get("published_date"),
                            src.get("relevance_score"),
                        )
                    )
        await db.commit()


# ─── Full Pipeline ────────────────────────────────────────────────────────────

async def run_evaluation_pipeline(evaluation_id: str, request: EvaluationRequest):
    """Runs in the background after the evaluation ID has been returned."""
    try:
        # Stage 1–2: send the same task to every selected model
        await _update_status(evaluation_id, "sending_to_models")
        logger.info(f"[{evaluation_id}] Sending task to models: {request.model_ids}")

        system_prompt = None
        if request.custom_instructions:
            system_prompt = f"Instructions: {request.custom_instructions}"

        model_results = await call_models_concurrently(
            model_ids=request.model_ids,
            task=request.task,
            max_tokens=request.max_tokens,
            system_prompt=system_prompt,
        )

        await _update_status(evaluation_id, "collecting_responses")
        failed_ids = [m for m, r in model_results.items() if _model_failed(r)]
        ok_ids = [m for m in model_results if m not in failed_ids]
        logger.info(f"[{evaluation_id}] Model responses: {len(ok_ids)} ok, {len(failed_ids)} failed")

        # Save every model's real outcome (including real error messages)
        async with aiosqlite.connect(DB_PATH) as db:
            for model_id, result in model_results.items():
                failed = _model_failed(result)
                error_text = result.get("error")
                if failed and not error_text:
                    error_text = "Empty response from provider."
                await db.execute(
                    """INSERT INTO model_responses
                       (evaluation_id, model_id, response_text, status, error_message,
                        latency_ms, prompt_tokens, completion_tokens, total_tokens,
                        estimated_cost_usd, finish_reason, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        evaluation_id,
                        model_id,
                        None if failed else result.get("response_text"),
                        "failed" if failed else "completed",
                        error_text if failed else None,
                        result.get("latency_ms"),
                        result.get("prompt_tokens"),
                        result.get("completion_tokens"),
                        result.get("total_tokens"),
                        result.get("estimated_cost_usd"),
                        result.get("finish_reason"),
                        datetime.utcnow().isoformat() + "Z",
                    )
                )
            await db.commit()

        # If nothing answered, stop here with an honest status.
        if not ok_ids:
            reasons = "; ".join(
                f"{m}: {model_results[m].get('error') or 'empty response'}" for m in failed_ids
            )
            message = f"All models failed. {reasons}"[:1500]
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute(
                    "UPDATE evaluations SET status = ?, error_message = ?, completed_at = ? WHERE id = ?",
                    ("failed", message, datetime.utcnow().isoformat() + "Z", evaluation_id)
                )
                await db.commit()
            logger.error(f"[{evaluation_id}] {message}")
            return

        judge_model = _pick_judge_model(request.model_ids, model_results)
        max_claims = _max_claims()
        analysis_errors: dict[str, str] = {}

        # Stage 3: extract claims (valid responses only)
        await _update_status(evaluation_id, "extracting_claims")
        all_model_claims: dict[str, list] = {m: [] for m in model_results}

        for model_id in ok_ids:
            try:
                claims = await extract_claims(model_results[model_id]["response_text"], judge_model)
                claims = (claims or [])[:max_claims]
                all_model_claims[model_id] = claims
                logger.info(f"[{evaluation_id}] {model_id}: extracted {len(claims)} claims")
                await _store_claims(evaluation_id, model_id, claims)
            except Exception as exc:
                analysis_errors[model_id] = f"Claim extraction failed: {exc}"
                logger.error(f"[{evaluation_id}] {model_id}: {analysis_errors[model_id]}", exc_info=True)

        # Stage 4–5: search evidence + verify (only models with claims)
        await _update_status(evaluation_id, "searching_evidence")
        all_verified_claims: dict[str, list] = {m: [] for m in model_results}

        for model_id, claims in all_model_claims.items():
            if not claims:
                continue
            try:
                await _update_status(evaluation_id, "verifying_claims")
                verified = await verify_claims_batch(claims, judge_model)
                all_verified_claims[model_id] = verified or []
                logger.info(f"[{evaluation_id}] {model_id}: verified {len(all_verified_claims[model_id])} claims")
                await _store_verified_claims(evaluation_id, model_id, all_verified_claims[model_id])
            except Exception as exc:
                analysis_errors[model_id] = f"Claim verification failed: {exc}"
                logger.error(f"[{evaluation_id}] {model_id}: {analysis_errors[model_id]}", exc_info=True)

        # Stage 6: scores
        await _update_status(evaluation_id, "calculating_scores")

        for model_id, result in model_results.items():
            model_failed = model_id in failed_ids
            verified_claims = all_verified_claims.get(model_id, [])

            status_counts = {
                "SUPPORTED": 0, "CONTRADICTED": 0,
                "POTENTIALLY_OUTDATED": 0, "UNVERIFIABLE": 0, "OPINION": 0,
            }
            for c in verified_claims:
                v_status = (c.get("verification") or {}).get("status", "UNVERIFIABLE")
                if v_status in status_counts:
                    status_counts[v_status] += 1

            task_comp_score, _ = calculate_task_completion(result.get("response_text"), request.task)

            if model_failed:
                trust_score, efficiency_score = None, None
                trust_explanation = (
                    f"Not scored: the model failed ({result.get('error') or 'empty response'}). "
                    f"There was no answer to verify."
                )
                efficiency_explanation = "Not scored: the model failed, so there is no valid response to rate."
            else:
                efficiency_score, efficiency_explanation = calculate_efficiency_score(
                    latency_ms=result.get("latency_ms"),
                    total_tokens=result.get("total_tokens"),
                    estimated_cost_usd=result.get("estimated_cost_usd"),
                )
                if model_id in analysis_errors:
                    trust_score = None
                    trust_explanation = f"Not scored: {analysis_errors[model_id]}"
                else:
                    trust_score, trust_explanation = calculate_trust_score(
                        verified_count=status_counts["SUPPORTED"],
                        contradicted_count=status_counts["CONTRADICTED"],
                        outdated_count=status_counts["POTENTIALLY_OUTDATED"],
                        unverifiable_count=status_counts["UNVERIFIABLE"],
                        opinion_count=status_counts["OPINION"],
                        total_claims=len(verified_claims),
                        task_completion_score=task_comp_score,
                    )

            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute(
                    """INSERT INTO scores
                       (evaluation_id, model_id, trust_score, efficiency_score,
                        task_completion_score, verified_claims, contradicted_claims,
                        outdated_claims, unverifiable_claims, opinion_claims,
                        total_claims, trust_score_explanation, efficiency_score_explanation)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        evaluation_id, model_id,
                        trust_score, efficiency_score, task_comp_score,
                        status_counts["SUPPORTED"], status_counts["CONTRADICTED"],
                        status_counts["POTENTIALLY_OUTDATED"], status_counts["UNVERIFIABLE"],
                        status_counts["OPINION"], len(verified_claims),
                        trust_explanation, efficiency_explanation,
                    )
                )
                await db.commit()

        # Stage 7: final, honest status
        await _update_status(evaluation_id, "generating_report")

        if not failed_ids and not analysis_errors:
            final_status, final_error = "completed", None
        else:
            final_status = "partial"
            problems = [f"{m}: {model_results[m].get('error') or 'empty response'}" for m in failed_ids]
            problems += [f"{m}: {e}" for m, e in analysis_errors.items()]
            final_error = ("Some steps failed. " + "; ".join(problems))[:1500]

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE evaluations SET status = ?, error_message = ?, completed_at = ? WHERE id = ?",
                (final_status, final_error, datetime.utcnow().isoformat() + "Z", evaluation_id)
            )
            await db.commit()

        logger.info(f"[{evaluation_id}] Evaluation finished with status '{final_status}'.")

    except Exception as e:
        logger.error(f"[{evaluation_id}] Pipeline failed: {e}", exc_info=True)
        await _update_status(evaluation_id, "failed", str(e))


# ─── API Endpoints ────────────────────────────────────────────────────────────

@router.post("/evaluations", response_model=EvaluationResponse)
async def create_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
):
    """Start a new evaluation. Returns the ID immediately; the pipeline runs in the background."""
    if len(request.model_ids) < 2:
        raise HTTPException(status_code=400, detail="Please select at least 2 models to compare.")

    from routers.models import ALL_MODELS, _is_key_configured
    known_model_ids = {m["id"] for m in ALL_MODELS}
    for model_id in request.model_ids:
        if model_id not in known_model_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown model: {model_id}. See /api/models for available models.",
            )

    unavailable = []
    for model_id in request.model_ids:
        model_info = next((m for m in ALL_MODELS if m["id"] == model_id), None)
        if model_info and not _is_key_configured(model_info["env_key"]):
            unavailable.append(f"{model_id} (requires {model_info['env_key']})")

    if unavailable:
        raise HTTPException(
            status_code=400,
            detail=f"The following models are unavailable — missing API keys: {', '.join(unavailable)}. "
                   f"Set the required keys in backend/.env",
        )

    evaluation_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO evaluations
               (id, task, task_category, custom_instructions, max_tokens, status, demo_mode, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                evaluation_id,
                request.task,
                request.task_category,
                request.custom_instructions,
                request.max_tokens,
                "pending",
                False,
                created_at,
            )
        )
        for model_id in request.model_ids:
            model_info = next((m for m in ALL_MODELS if m["id"] == model_id), None)
            await db.execute(
                """INSERT INTO evaluation_models (evaluation_id, model_id, provider, display_name)
                   VALUES (?, ?, ?, ?)""",
                (
                    evaluation_id,
                    model_id,
                    model_info["provider"] if model_info else "unknown",
                    model_info["display_name"] if model_info else model_id,
                )
            )
        await db.commit()

    background_tasks.add_task(run_evaluation_pipeline, evaluation_id, request)

    return EvaluationResponse(
        evaluation_id=evaluation_id,
        status="pending",
        message="Evaluation started. Poll /api/evaluations/{id} for status updates.",
    )


@router.get("/evaluations/demo")
async def get_demo_evaluation_endpoint():
    """Return the pre-prepared demo evaluation. Clearly labelled as demo data."""
    return get_demo_evaluation()


@router.get("/evaluations/{evaluation_id}")
async def get_evaluation(evaluation_id: str):
    """Evaluation status and whatever results exist so far."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT * FROM evaluations WHERE id = ?", (evaluation_id,)) as cursor:
            eval_row = await cursor.fetchone()

        if not eval_row:
            raise HTTPException(status_code=404, detail=f"Evaluation {evaluation_id} not found.")

        eval_data = dict(eval_row)

        async with db.execute(
            "SELECT * FROM model_responses WHERE evaluation_id = ?", (evaluation_id,)
        ) as cursor:
            responses = [dict(r) for r in await cursor.fetchall()]

        async with db.execute(
            "SELECT * FROM scores WHERE evaluation_id = ?", (evaluation_id,)
        ) as cursor:
            scores = {r["model_id"]: dict(r) for r in await cursor.fetchall()}

        model_claims = {}
        async with db.execute(
            "SELECT * FROM claims WHERE evaluation_id = ? ORDER BY model_id, claim_index",
            (evaluation_id,)
        ) as cursor:
            claim_rows = await cursor.fetchall()

        for claim_row in claim_rows:
            claim = dict(claim_row)
            model_id = claim["model_id"]

            async with db.execute(
                "SELECT * FROM verification_results WHERE claim_id = ?", (claim["id"],)
            ) as cursor:
                ver_row = await cursor.fetchone()

            if ver_row:
                ver = dict(ver_row)
                async with db.execute(
                    "SELECT * FROM evidence_sources WHERE verification_id = ?", (ver["id"],)
                ) as cursor:
                    ver["sources"] = [dict(s) for s in await cursor.fetchall()]
                claim["verification"] = ver
            else:
                claim["verification"] = None

            model_claims.setdefault(model_id, []).append(claim)

        from routers.models import ALL_MODELS
        model_results = []
        for resp in responses:
            model_id = resp["model_id"]
            model_info = next((m for m in ALL_MODELS if m["id"] == model_id), None)
            score = scores.get(model_id, {})
            model_results.append({
                **resp,
                "display_name": model_info["display_name"] if model_info else model_id,
                "provider": model_info["provider"] if model_info else "unknown",
                "truncated": resp.get("finish_reason") == "length",
                "trust_score": score.get("trust_score"),
                "efficiency_score": score.get("efficiency_score"),
                "task_completion_score": score.get("task_completion_score"),
                "verified_claims": score.get("verified_claims", 0),
                "contradicted_claims": score.get("contradicted_claims", 0),
                "outdated_claims": score.get("outdated_claims", 0),
                "unverifiable_claims": score.get("unverifiable_claims", 0),
                "opinion_claims": score.get("opinion_claims", 0),
                "total_claims": score.get("total_claims", 0),
                "trust_score_explanation": score.get("trust_score_explanation"),
                "efficiency_score_explanation": score.get("efficiency_score_explanation"),
                "claims": model_claims.get(model_id, []),
            })

        return {
            **eval_data,
            "models": model_results,
        }


@router.get("/evaluations/{evaluation_id}/report")
async def get_evaluation_report(evaluation_id: str):
    """Full Trust Report. Available once the pipeline has finished (completed, partial or failed)."""
    eval_data = await get_evaluation(evaluation_id)

    if eval_data["status"] not in ("completed", "partial", "failed", "generating_report"):
        raise HTTPException(
            status_code=202,
            detail=f"Report not ready. Current status: {eval_data['status']}",
        )

    report = generate_report(
        evaluation_id=evaluation_id,
        task=eval_data["task"],
        task_category=eval_data.get("task_category", "General"),
        model_results=eval_data["models"],
    )
    return report

