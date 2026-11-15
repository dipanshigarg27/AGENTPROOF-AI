'''
AgentProof AI — Claim Extractor Service
Extracts and classifies factual claims from AI model responses using an LLM.
'''

import json
import logging
import re
from typing import Optional

logger = logging.getLogger("agentproof.claims")

# ---------------------------------------------------------------------------
# Claim types – kept identical to the original list for compatibility
# ---------------------------------------------------------------------------
CLAIM_TYPES = [
    "time_sensitive_factual",   # e.g., "The current interest rate is X%"
    "historical_factual",       # e.g., "World War II ended in 1945"
    "general_factual",          # e.g., "Water boils at 100°C"
    "opinion",                  # e.g., "This approach is better"
    "prediction",               # e.g., "AI will transform healthcare"
]

# ---------------------------------------------------------------------------
# Prompt sent to the LLM for claim extraction. The prompt itself is unchanged
# except that we now ask the model to ignore markdown formatting.
# ---------------------------------------------------------------------------
EXTRACTION_PROMPT = """You are a precise fact-checking assistant. Extract individual factual claims from the AI response below.

For each claim, return:
1. The exact claim text (a single sentence or short phrase)
2. The claim type (one of: time_sensitive_factual, historical_factual, general_factual, opinion, prediction)

Rules:
- Only extract clear, specific claims — not vague statements
- Do NOT invent claims not in the text
- Opinions and predictions should be labelled as such, not as factual claims
- Extract at most 10 claims per response
- Return JSON only — no preamble

Return this exact JSON format:
{
  "claims": [
    {"text": "claim text here", "type": "time_sensitive_factual"},
    {"text": "another claim", "type": "general_factual"}
  ]
}

AI Response to analyze:
"""

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _clean_claim_text(text: str) -> str:
    """Strip markdown symbols, headings, bullet markers, numbering, tables, and code fences.
    Returns a trimmed plain‑text claim.
    """
    # Remove full markdown headings (e.g., "# Heading" or "## Sub‑heading")
    text = re.sub(r"^#{1,6}\s.*$", "", text, flags=re.MULTILINE)
    # Remove horizontal rules consisting of three or more dashes, asterisks, or underscores
    text = re.sub(r"^\s*([-*_]){3,}\s*$", "", text, flags=re.MULTILINE)
    # Remove list markers ("-", "*", "+") and any surrounding whitespace
    text = re.sub(r"^[\s]*[-*+]\s+", "", text, flags=re.MULTILINE)
    # Remove numbered list prefixes ("1.", "2)", "3]")
    text = re.sub(r"^[\s]*\d+[\.)\]]\s+", "", text, flags=re.MULTILINE)
    # Remove table rows or pipe separators
    text = re.sub(r"\|", " ", text)
    # Remove fenced code blocks and inline backticks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)  # triple backticks
    text = re.sub(r"`{1,3}.*?`{1,3}", "", text)            # inline code
    # Remove remaining markdown formatting characters (` * _ ~)
    text = re.sub(r"[`*_~]", "", text)
    # Collapse multiple spaces and strip
    text = re.sub(r"\s+", " ", text).strip()
    return text
    """Strip markdown symbols, headings, bullet markers, numbering, tables, and code fences.
    Returns a trimmed plain‑text claim.
    """
    # Remove leading markdown headings (e.g., "# Heading") and horizontal rules
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    # Remove list markers ("-", "*", "+") and any surrounding whitespace
    text = re.sub(r"^[\s]*[-*+]\s+", "", text, flags=re.MULTILINE)
    # Remove numbered list prefixes ("1.", "2)", "3]")
    text = re.sub(r"^[\s]*\d+[\.)\]]\s+", "", text, flags=re.MULTILINE)
    # Remove table rows or pipe separators
    text = re.sub(r"\|", " ", text)
    # Remove markdown horizontal rules composed of *** or ___
    text = re.sub(r"^([*_-]{3,})$", "", text, flags=re.MULTILINE)
    # Remove fenced code blocks and inline backticks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)  # triple backticks
    text = re.sub(r"`{1,3}.*?`{1,3}", "", text)            # inline code
    # Remove remaining markdown formatting characters (` * _ ~)
    text = re.sub(r"[`*_~]", "", text)
    # Collapse multiple spaces and strip
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_duplicate(claim_text: str, seen: set) -> bool:
    norm = claim_text.lower()
    if norm in seen:
        return True
    seen.add(norm)
    return False


def _split_compound_claims(text: str) -> list[str]:
    """Conservatively split a claim that contains multiple independent statements.
    Splits on ';' unconditionally. For ' and ' / ' but ', split only when both sides
    appear to be self‑contained statements (start with a capital letter and are at
    least 8 characters long). Ensures each returned fragment ends with a period.
    """
    parts = [text]
    # First split on semicolons – these are a strong indicator of separate clauses
    new_parts = []
    for part in parts:
        if ";" in part:
            segments = [seg.strip() for seg in part.split(";") if seg.strip()]
            new_parts.extend(segments)
        else:
            new_parts.append(part)
    parts = new_parts

    # Helper to decide whether a fragment looks like a standalone claim
    def looks_independent(fragment: str) -> bool:
        return (
            len(fragment) >= 8
            and fragment[0].isupper()
        )

    # Attempt to split on conjunctions only when both halves look independent
    conjunctions = [r"\band\b", r"\bbut\b"]
    verb_cues = ["is", "are", "was", "were", "will", "should", "could", "might", "must", "have", "has", "did", "does", "did"]
    def contains_verb(fragment: str) -> bool:
        words = fragment.lower().split()
        return any(v in words for v in verb_cues)
    for conj in conjunctions:
        new_parts = []
        for part in parts:
            if re.search(conj, part, flags=re.IGNORECASE):
                # split on the first occurrence only to avoid over‑splitting
                left, right = re.split(conj, part, maxsplit=1, flags=re.IGNORECASE)
                left, right = left.strip(), right.strip()
                # Split if both look independent or both contain verb cues
                if (looks_independent(left) and looks_independent(right)) or (contains_verb(left) and contains_verb(right)):
                    new_parts.append(left)
                    new_parts.append(right)
                    continue
            new_parts.append(part)
        parts = new_parts
    conjunctions = [r"\band\b", r"\bbut\b"]
    for conj in conjunctions:
        new_parts = []
        for part in parts:
            if re.search(conj, part, flags=re.IGNORECASE):
                # split on the first occurrence only to avoid over‑splitting
                left, right = re.split(conj, part, maxsplit=1, flags=re.IGNORECASE)
                left, right = left.strip(), right.strip()
                if looks_independent(left) and looks_independent(right):
                    new_parts.append(left)
                    new_parts.append(right)
                    continue
            new_parts.append(part)
        parts = new_parts

    # Ensure each fragment ends with a period for consistency
    finalized = []
    for frag in parts:
        frag = frag.strip()
        if not frag:
            continue
        if not frag.endswith(('.', '!', '?')):
            frag = frag + '.'
        finalized.append(frag)
    return finalized
    """Conservatively split a claim that contains multiple independent statements.
    Splits on ';' unconditionally. For ' and ' / ' but ', split only when both sides
    appear to be self‑contained statements (start with a capital letter and are at
    least 8 characters long).
    """
    parts = [text]
    # First split on semicolons – these are a strong indicator of separate clauses
    new_parts = []
    for part in parts:
        if ";" in part:
            segments = [seg.strip() for seg in part.split(";") if seg.strip()]
            new_parts.extend(segments)
        else:
            new_parts.append(part)
    parts = new_parts

    # Helper to decide whether a fragment looks like a standalone claim
    def looks_independent(fragment: str) -> bool:
        return (
            len(fragment) >= 8
            and fragment[0].isupper()
        )

    # Attempt to split on conjunctions only when both halves look independent
    conjunctions = [r"\band\b", r"\bbut\b"]
    verb_cues = ["is", "are", "was", "were", "will", "should", "could", "might", "must", "have", "has", "did", "does", "did"]
    def contains_verb(fragment: str) -> bool:
        words = fragment.lower().split()
        return any(v in words for v in verb_cues)
    for conj in conjunctions:
        new_parts = []
        for part in parts:
            if re.search(conj, part, flags=re.IGNORECASE):
                # split on the first occurrence only to avoid over‑splitting
                left, right = re.split(conj, part, maxsplit=1, flags=re.IGNORECASE)
                left, right = left.strip(), right.strip()
                # Split if both look independent or both contain verb cues
                if (looks_independent(left) and looks_independent(right)) or (contains_verb(left) and contains_verb(right)):
                    new_parts.append(left)
                    new_parts.append(right)
                    continue
            new_parts.append(part)
        parts = new_parts
    conjunctions = [r"\band\b", r"\bbut\b"]
    for conj in conjunctions:
        new_parts = []
        for part in parts:
            if re.search(conj, part, flags=re.IGNORECASE):
                # split on the first occurrence only to avoid over‑splitting
                left, right = re.split(conj, part, maxsplit=1, flags=re.IGNORECASE)
                left, right = left.strip(), right.strip()
                if looks_independent(left) and looks_independent(right):
                    new_parts.append(left)
                    new_parts.append(right)
                    continue
            new_parts.append(part)
        parts = new_parts
    return parts

# ---------------------------------------------------------------------------
# Main extraction function – asynchronous because it may call the LLM service
# ---------------------------------------------------------------------------
async def extract_claims(response_text: str, model_id: str = "openai/gpt-4o-mini") -> list[dict]:
    """Extract factual claims from an AI model response.

    The function first attempts LLM‑based extraction. If that fails, it falls back to a
    simple heuristic sentence splitter. Only factual claims are returned; opinions,
    predictions and other non‑factual items are kept but labelled with their type so the
    verification pipeline can filter them out.
    """
    if not response_text or len(response_text.strip()) < 20:
        return []

    # ---------------------------------------------------------------
    # 1️⃣ Pre‑process the raw response to remove obvious markdown
    # ---------------------------------------------------------------
    preprocessed = response_text
    # Remove headings, bullet points, numbered lists and table rows (basic fast pass)
    preprocessed = re.sub(r"^#{1,6}.*$", "", preprocessed, flags=re.MULTILINE)
    preprocessed = re.sub(r"^[\s]*[-*+]\s+", "", preprocessed, flags=re.MULTILINE)
    preprocessed = re.sub(r"^[\s]*\d+[\.)\]]\s+", "", preprocessed, flags=re.MULTILINE)
    preprocessed = re.sub(r"^\s*\|.*\|\s*$", "", preprocessed, flags=re.MULTILINE)

    try:
        from services.bifrost_service import call_model
        result = await call_model(
            model_id=model_id,
            task=EXTRACTION_PROMPT + preprocessed[:3000],
            max_tokens=1500,
        )

        if result.get("error") or not result.get("response_text"):
            raise ValueError(f"LLM extraction failed: {result.get('error')}")

        raw = result["response_text"].strip()
        # Grab the JSON object – guard against markdown code fences
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)
        parsed = json.loads(raw)
        raw_claims = parsed.get("claims", [])

        claims = []
        seen = set()
        for i, claim in enumerate(raw_claims[:10]):  # safety cap
            if isinstance(claim, dict) and "text" in claim and "type" in claim:
                cleaned = _clean_claim_text(str(claim["text"]))
                if not cleaned or len(cleaned) < 10:
                    continue  # skip empty/very short fragments
                # Split compound statements conservatively
                sub_parts = _split_compound_claims(cleaned)
                for sub in sub_parts:
                    sub = sub.strip()
                    if not sub or len(sub) < 10:
                        continue
                    if _is_duplicate(sub, seen):
                        continue
                    claim_type = claim["type"] if claim["type"] in CLAIM_TYPES else "general_factual"
                    claims.append({
                        "text": sub,
                        "type": claim_type,
                        "claim_index": i,
                    })
        # Enforce the overall 10‑claim limit after possible splitting
        claims = claims[:10]
        logger.info(f"Extracted {len(claims)} claims from response")
        return claims

    except Exception as e:
        logger.warning(f"LLM extraction failed, falling back to simple extraction: {e}")
        return _simple_extract(response_text)

# ---------------------------------------------------------------------------
# Simple fallback extraction – operates on plain sentences
# ---------------------------------------------------------------------------
def _simple_extract(text: str) -> list[dict]:
    """Fallback: split into sentences, clean, deduplicate, and label.
    This path is used when the LLM service is unavailable.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    claims = []
    seen = set()

    # Keyword lists for lightweight opinion/prediction detection
    opinion_cues = ["i think", "i believe", "in my opinion", "we think", "we believe", "it seems", "should", "could", "might", "would", "maybe", "perhaps"]
    prediction_cues = ["will", "going to", "expect", "forecast", "project", "anticipate", "likely", "probably"]

    for i, sent in enumerate(sentences[:12]):  # a modest limit before final truncation
        cleaned = _clean_claim_text(sent.strip())
        if len(cleaned) <= 20:
            continue
        # Split possible compound statements
        sub_parts = _split_compound_claims(cleaned)
        for sub in sub_parts:
            sub = sub.strip()
            if not sub:
                continue
            lower = sub.lower()
            # Determine claim type conservatively
            if any(cue in lower for cue in opinion_cues):
                claim_type = "opinion"
            elif any(cue in lower for cue in prediction_cues):
                claim_type = "prediction"
            else:
                claim_type = "time_sensitive_factual" if any(
                    w in lower for w in ["current", "latest", "today", "now", "recently", "2024", "2025"]
                ) else "general_factual"
            if _is_duplicate(sub, seen):
                continue
            claims.append({"text": sub, "type": claim_type, "claim_index": i})
            if len(claims) >= 10:
                break
        if len(claims) >= 10:
            break
    return claims
